import voyageai
from pinecone import Pinecone, ServerlessSpec
from rid_lib.core import RID

from .config import (
    VOYAGEAI_API_KEY, 
    PINECONE_API_KEY, 
    PINECONE_CLOUD_PROVIDER,
    PINECONE_CLOUD_REGION,
    PINECONE_INDEX_NAME,
    PINECONE_INDEX_METRIC,
    PINECONE_BATCH_SIZE,
    EMBEDDINGS_DIMENSION, 
    VOYAGEAI_MODEL, 
    VOYAGEAI_BATCH_SIZE,
    MAX_CHUNK_SIZE,
    CHUNK_OVERLAP
)


pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
voyageai_client = voyageai.Client(api_key=VOYAGEAI_API_KEY)

def setup_pinecone_index():
    if PINECONE_INDEX_NAME not in pinecone_client.list_indexes().names():
        pinecone_client.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDINGS_DIMENSION,
            spec=ServerlessSpec(
                cloud=PINECONE_CLOUD_PROVIDER,
                region=PINECONE_CLOUD_REGION
            ),
            metric=PINECONE_INDEX_METRIC
        )
    
    return pinecone_client.Index(PINECONE_INDEX_NAME)


class VectorObject:
    pinecone_index = setup_pinecone_index()
    embedding_queue = []
    queue_limit = 100

    def __init__(self, rid: RID):
        self.rid = rid            

    def embed(self, flush_queue=False):
        cached_object = self.rid.cache.read()

        if cached_object.json_data is None or "text" not in cached_object.json_data:
            print("cache empty or missing text field, can't embed")
            return False
        
        text = cached_object.json_data["text"]
        meta = cached_object.metadata
        del meta["files"]
        meta["text"] = text

        if len(text) > MAX_CHUNK_SIZE:
            start = 0
            end = MAX_CHUNK_SIZE
            count = 0
            while start < len(text):
                rid_fragment = f"{self.rid}#chunk:{count}"
                chunk_text = text[start:end]
                chunk_meta = {
                    **meta,
                    "character_length": len(chunk_text),
                    "text": chunk_text,
                    "chunk_start": start,
                    "chunk_end": end
                }

                print(f"adding {rid_fragment} to embedding queue")

                self.embedding_queue.append([
                    rid_fragment, chunk_text, chunk_meta
                ])

                start += (MAX_CHUNK_SIZE - CHUNK_OVERLAP)
                end = start + MAX_CHUNK_SIZE
                count += 1

        else:
            print(f"adding {self.rid} to embedding queue")

            self.embedding_queue.append([
                str(self.rid), text, meta
            ])

        if flush_queue is True or len(self.embedding_queue) > self.queue_limit:
            self.embed_queue()

    @classmethod
    def embed_queue(cls):
        print(f"flushing {len(cls.embedding_queue)} objects from embedding queue")

        ids, texts, metas = list(zip(*cls.embedding_queue))

        embeddings = []
        while len(embeddings) < len(cls.embedding_queue):
            start = len(embeddings)
            end = min(start + VOYAGEAI_BATCH_SIZE, len(cls.embedding_queue))
            embeddings.extend(
                voyageai_client.embed(
                    texts=texts[start:end],
                    model=VOYAGEAI_MODEL,
                    input_type="document"
                ).embeddings
            )
            print(f"created embeddings for {end} objects")

        print(f"resulting in {len(embeddings)} embeddings")
        
        vectors = list(zip(
            ids, embeddings, metas
        ))

        cls.pinecone_index.upsert(
            vectors=vectors, batch_size=PINECONE_BATCH_SIZE
        )
        print(f"upserted {len(vectors)} objects")
        cls.embedding_queue = []

    def read(self):
        return self.pinecone_index.fetch([str(self.rid)])

    def delete(self):
        return self.pinecone_index.delete([str(self.rid)])




pc = Pinecone(api_key=PINECONE_API_KEY)
vc = voyageai.Client(api_key=VOYAGEAI_API_KEY)

if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        PINECONE_INDEX_NAME,
        dimension=EMBEDDINGS_DIMENSION,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        metric="cosine"
    )

index = pc.Index(PINECONE_INDEX_NAME)

def get_num_chunks(total_char_len, chunk_size=MAX_CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    import math
    chunk_step = chunk_size - chunk_overlap
    return math.ceil((total_char_len - chunk_overlap) / chunk_step)

def get_chunk_offset(chunk_id, chunk_size=MAX_CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    chunk_step = chunk_size - chunk_overlap
    return chunk_id * chunk_step
    

def create_embeddings(docs: list[str]):
    embeddings = []
    while len(embeddings) < len(docs):
        i = len(embeddings)
        embeddings.extend(
            vc.embed(
                texts=docs[i:i+VOYAGEAI_BATCH_SIZE],
                model=VOYAGEAI_MODEL,
                input_type="document"
            ).embeddings
        )
        print(f"created embeddings for {i+VOYAGEAI_BATCH_SIZE} objects")
    return embeddings

def embed_objects(rids: list[RID]):
    total_rids = len(rids)
    accepted_rids = 0

    objects = []
    for rid in rids:
        cached_object = rid.cache.read()
        
        if cached_object.json_data is None:
            continue
        
        text = cached_object.json_data.get("text")

        meta = cached_object.metadata
        del meta["files"]
        meta["text"] = text

        if not text:
            continue

        if len(text) > MAX_CHUNK_SIZE:
            num_chunks = get_num_chunks(len(text))
            for chunk_id in range(num_chunks):
                start = get_chunk_offset(chunk_id)
                end = min(start + MAX_CHUNK_SIZE, len(text))

                print(f"slice {start}:{end}")

                text_chunk = text[start:end]

                rid_fragment = f"{rid}#chunk:{chunk_id}"

                chunk_meta = {
                    **meta,
                    "character_length": len(text_chunk),
                    "chunk_id": chunk_id,
                    "total_chunks": num_chunks,
                    "chunk_size": MAX_CHUNK_SIZE,
                    "chunk_overlap": CHUNK_OVERLAP,
                    "text": text_chunk
                }

                objects.append([
                    rid_fragment, text_chunk, chunk_meta
                ])

            print(f"{rid} split into {num_chunks} chunks")

        else:
            objects.append([
                str(rid), text, meta
            ])
            print(f"{rid}")

        accepted_rids += 1

    print(f"{accepted_rids}/{total_rids} processed resulting in {len(objects)} objects")

    if not objects:
        return

    # converting object texts to embeddings
    ids, texts, metas = list(zip(*objects))
    vectors = list(zip(
        ids, create_embeddings(texts), metas
    ))

    index.upsert(vectors, batch_size=VOYAGEAI_BATCH_SIZE)
    print(f"upserted {len(vectors)} objects")
    print(index.describe_index_stats())
    

def query_ids(text):
    query_embedding = vc.embed(
        texts=[text],
        model=VOYAGEAI_MODEL,
        input_type="query",
    ).embeddings

    result = index.query(
        vector=query_embedding, 
        filter={
            "character_length": {"$gt": 200}
        },
        top_k=7, 
        include_metadata=True
    )

    return [(m["id"], m["score"]) for m in result["matches"]]

def query(text):
    docs = []
    for id, score in query_ids(text):
        components = id.rsplit("#", 1)
        if len(components) == 1:
            rid_str, = components
            chunk_str = None
        else:
            rid_str, chunk_str = components

        rid = RID.from_string(rid_str)

        cached_obj = rid.cache.read()
        if cached_obj.empty:
            print(f"{rid} retrieved from vectorstore, but cache not found")
            continue

        text = cached_obj.json_data["text"]

        if chunk_str:
            chunk_id = int(chunk_str.split(":")[1])
            start = get_chunk_offset(chunk_id)
            end = min(len(text), start + MAX_CHUNK_SIZE)
            print(f"slicing rid {rid} chunk {chunk_id} at {start}:{end}")
            text = text[start:end]

        docs.append([rid, text, chunk_id])
    return docs


def read(rids):
    return index.fetch([str(rid) for rid in rids])

def delete(rids):
    return index.delete([str(rid) for rid in rids])

def drop():
    index.delete(list(index.list()))

def scrub():
    rids = []
    for ids in index.list():
        rids.extend([RID.from_string(id) for id in ids])

    to_delete = []
    for rid in rids:
        if not rid.cache.read().json_data:
            print(rid)
            to_delete.append(str(rid))
    
    index.delete(to_delete)