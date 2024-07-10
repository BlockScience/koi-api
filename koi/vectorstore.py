import voyageai
from pinecone import Pinecone, ServerlessSpec
from rid_lib.core import RID

from .config import (
    VOYAGEAI_API_KEY, 
    PINECONE_API_KEY, 
    PINECONE_INDEX_NAME, 
    EMBEDDINGS_DIMENSION, 
    VOYAGEAI_MODEL, 
    VOYAGEAI_BATCH_SIZE,
    MAX_CHUNK_SIZE,
    CHUNK_OVERLAP
)


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
    

def embed_objects_old(rids: list[RID]):
    ids = []
    texts = []
    meta = []
    
    for rid in rids:
        cached_object = rid.cache.read()

        if cached_object.json_data is None:
            continue

        text = cached_object.json_data.get("text")

        if not text:
            # print("deleting empty rid:", str(rid))
            # delete(rid)
            continue
        
        prefix_embedding = cached_object.json_data.get("prefix_embedding", None)
        if prefix_embedding:
            text = prefix_embedding + text

        print(f"embedding {str(rid)}")
        
        ids.append(str(rid))
        texts.append(text)
        meta.append({
            "sha256_hash": cached_object.metadata.get("sha256_hash"),
            "character_length": len(text),
            "space": rid.space,
            "format": rid.format,
            "text": text
        })

    embeddings = []
    while len(embeddings) < len(texts):
        embeddings.extend(
            vc.embed(
                texts=texts[len(embeddings):len(embeddings)+VOYAGEAI_BATCH_SIZE],
                model=VOYAGEAI_MODEL,
                input_type="document"
            ).embeddings
        )
        print(f"embedded {len(embeddings)}/{len(texts)} documents")

    print("done embedding.")

    print(len(ids), len(texts), len(embeddings), len(meta))

    vectors = list(zip(
        ids, embeddings, meta
    ))

    print("beginning upsert")

    for i in range(0, len(vectors), VOYAGEAI_BATCH_SIZE):
        step = min(i+VOYAGEAI_BATCH_SIZE, len(vectors))
        index.upsert(vectors=vectors[i:step])
        print(f"upserted {step} documents")

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