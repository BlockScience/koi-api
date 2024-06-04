import voyageai
from pinecone import Pinecone, ServerlessSpec
import numpy as np
from .config import VOYAGEAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDINGS_DIMENSION, VOYAGEAI_MODEL, VOYAGEAI_BATCH_SIZE
from . import cache

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
        data, hash = cache.read(rid)
        text = data["text"]
        
        texts.append(text)
        meta.append({
            "sha256_hash": hash,
            "character_length": len(text),
            "space": rid.space,
            "format": rid.format
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
            "character_length": {"$gt": 250}
        },
        top_k=5, 
        include_metadata=True
    )

    return [(m["id"], m["score"]) for m in result["matches"]]