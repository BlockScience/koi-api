import voyageai
from pinecone import Pinecone, ServerlessSpec
from rid_lib import RID

from .config import (
    VOYAGEAI_API_KEY, 
    PINECONE_API_KEY, 
    PINECONE_INDEX_NAME, 
    EMBEDDINGS_DIMENSION, 
    VOYAGEAI_MODEL, 
    VOYAGEAI_BATCH_SIZE
)
from . import cache, graph


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

def embed_objects(rids):
    ids = [str(rid) for rid in rids]
    texts = []
    meta = []
    
    for rid in rids:
        cached_object = cache.read(rid)

        if cached_object.data is None:
            continue

        text = cached_object.data.get("text")

        if not text:
            continue
        
        prefix_embedding = cached_object.data.get("prefix_embedding", None)
        if prefix_embedding:
            text = prefix_embedding + text

        print(f"embedding {str(rid)}:")
        print(text)
        
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
        print(f"embedded {len(embeddings)} documents")

    vectors = list(zip(
        ids, embeddings, meta
    ))

    for i in range(0, len(vectors), VOYAGEAI_BATCH_SIZE):
        step = min(i+VOYAGEAI_BATCH_SIZE, len(vectors))
        index.upsert(vectors=vectors[i:step])
        print(f"upserted {step} documents")

    print(index.describe_index_stats())

def query(text):
    query_embedding = vc.embed(
        texts=[text],
        model=VOYAGEAI_MODEL,
        input_type="query",
    ).embeddings

    result = index.query(
        vector=query_embedding, 
        filter={
            "character_length": {"$gt": 100}
        },
        top_k=20, 
        include_metadata=True
    )

    return [(m["id"], m["score"]) for m in result["matches"]]

def read(rid):
    return index.fetch([str(rid)])

def delete(rid):
    index.delete([str(rid)])

def scrub():
    rids = []
    for ids in index.list():
        rids.extend([RID.from_string(id) for id in ids])

    to_delete = []
    for rid in rids:
        if not cache.read(rid).data:
            to_delete.append(str(rid))
    
    index.delete(to_delete)