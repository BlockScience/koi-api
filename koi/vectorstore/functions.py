from .base import pinecone_index, voyage_embed_texts
from .vector_object import VectorObject


def query(text, top_k=10, filter={"character_length": {"$gt": 200}}):
    result = pinecone_index.query(
        vector=voyage_embed_texts([text], input_type="query"),
        filter=filter,
        top_k=top_k,
        include_metadata=True
    )
    vectors = result["matches"]

    return [
        VectorObject(v) for v in vectors
    ]

def drop():
    pinecone_index.delete(delete_all=True)