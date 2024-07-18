import voyageai
from pinecone import Pinecone, ServerlessSpec

from koi.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    EMBEDDINGS_DIMENSION,
    PINECONE_CLOUD_PROVIDER,
    PINECONE_CLOUD_REGION,
    PINECONE_INDEX_METRIC,
    VOYAGEAI_API_KEY,
    VOYAGEAI_MODEL
)

pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# creates serverless index if it doesn't exist yet
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


voyageai_client = voyageai.Client(api_key=VOYAGEAI_API_KEY)

# wrapper function to set constants and default params in one place
def voyage_embed_texts(texts, input_type="document"):
    return voyageai_client.embed(
        texts=texts,
        model=VOYAGEAI_MODEL,
        input_type=input_type,
        truncation=False
    ).embeddings
