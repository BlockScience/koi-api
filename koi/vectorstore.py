import voyageai
from pinecone import Pinecone, ServerlessSpec
from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


voyageai_client = voyageai.Client(api_key=VOYAGEAI_API_KEY)
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

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

pinecone_index = pinecone_client.Index(PINECONE_INDEX_NAME)


def chunkify_text(text):
    chunks = []
    if len(text) > CHUNK_SIZE:
        start = 0
        end = CHUNK_SIZE
        while start < len(text):
            chunks.append({
                "text": text[start:end],
                "start": start,
                "end": end
            })
            start += (CHUNK_SIZE - CHUNK_OVERLAP)
            end = start + CHUNK_SIZE
    else:
        chunks.append({
            "text": text
        })
    
    return chunks

def create_rid_fragment_string(rid, chunk_id):
    return f"{rid}#chunk:{chunk_id}"


class VectorObject:
    def __init__(
            self,
            rid: RID,
            vector: dict
        ):

        self.rid = rid
        self.values = vector["values"]
        self.metadata = vector["metadata"]
        self.is_chunk = "chunk_id" in self.metadata

        if self.is_chunk:
            self.chunk_id = int(vector["metadata"]["chunk_id"])
            self.chunk_start = int(self.metadata["chunk_start"])
            self.chunk_end = int(self.metadata["chunk_end"])

            self.id = create_rid_fragment_string(self.rid, self.chunk_id)
        
        else:
            self.id = str(self.rid)


    def get_text(self):
        cached_obj = self.rid.cache.read()
        text = cached_obj.json_data.get("text")
        if not text: return

        if self.is_chunk:
            return text[self.chunk_start:self.chunk_end]
        else:
            return text


class EmbeddableObject:
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

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        chunks = []
        for doc in text_splitter.create_documents([text]):
            chunk_text = doc.page_content
            start = text.find(chunk_text)
            end = start + len(chunk_text)
            chunks.append({
                "text": chunk_text,
                "start": start,
                "end": end
            })

        if len(chunks) == 1:
            self.embedding_queue.append([
                str(self.rid), text, meta
            ])
            print(f"added {self.rid} to embedding queue")

        else:
            for i, chunk in enumerate(chunks):
                rid_fragment = create_rid_fragment_string(self.rid, i)
                chunk_text = chunk["text"]
                chunk_meta = {
                    **meta,
                    "character_length": len(chunk_text),
                    "text": chunk_text,
                    "chunk_start": chunk["start"],
                    "chunk_end": chunk["end"],
                    "chunk_id": i,
                    "num_chunks": len(chunks)
                }

                print(f"{self.rid} chunk {i+1}/{len(chunks)} [{chunk['start']}:{chunk['end']}]")
                
                self.embedding_queue.append([
                    rid_fragment, chunk_text, chunk_meta
                ])
            print(f"added {self.rid} to embedding queue ({len(chunks)} chunks)")

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
        cls.embedding_queue = []

    def read(self):
        rid_fragment_str = create_rid_fragment_string(self.rid, 0)
        potential_ids = [
            str(self.rid),
            rid_fragment_str
        ]

        resp = pinecone_index.fetch(potential_ids)
        vectors = resp.to_dict()["vectors"]

        if str(self.rid) in vectors:
            return [
                VectorObject(self.rid, vectors[str(self.rid)])
            ]
        
        elif rid_fragment_str in vectors:
            obj = vectors[rid_fragment_str]
            num_chunks = int(obj["metadata"]["num_chunks"])

            chunk_ids = [
                create_rid_fragment_string(self.rid, i)
                for i in range(num_chunks)
            ]

            resp = pinecone_index.fetch(chunk_ids)
            chunk_vectors = resp.to_dict()["vectors"]

            return [
                VectorObject(self.rid, chunk_vectors[chunk_id])
                for chunk_id in chunk_ids
            ]

        else:
            return []

    def delete(self):
        return pinecone_index.delete([str(self.rid)])


def query_ids(text):
    query_embedding = voyageai_client.embed(
        texts=[text],
        model=VOYAGEAI_MODEL,
        input_type="query",
    ).embeddings

    result = pinecone_index.query(
        vector=query_embedding, 
        filter={
            "character_length": {"$gt": 200}
        },
        top_k=7, 
        include_metadata=True
    )

    return [(m["id"], m["score"], m["metadata"]) for m in result["matches"]]

def query(text):
    docs = []
    for id, score, metadata in query_ids(text):
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
            start = int(metadata["chunk_start"])
            end = int(metadata["chunk_end"])
            print(f"slicing rid {rid} chunk {chunk_id} at {start}:{end}")
            text = text[start:end]

        docs.append([rid, text, chunk_id])
    return docs


def drop():
    pinecone_index.delete(list(pinecone_index.list()))

def scrub():
    rids = []
    for ids in pinecone_index.list():
        rids.extend([RID.from_string(id) for id in ids])

    to_delete = []
    for rid in rids:
        if not rid.cache.read().json_data:
            print(rid)
            to_delete.append(str(rid))
    
    pinecone_index.delete(to_delete)