import os

from dotenv import load_dotenv


load_dotenv()

DEV = (os.getenv("DEV", "false").lower() == "true")

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "koi-pond")
NEO4J_DB = "neo4j" 

CACHE_DIRECTORY = "cache"

OPENAI_API_KEY = os.getenv["OPENAI_API_KEY"]

PINECONE_API_KEY = os.getenv["PINECONE_API_KEY"]
PINECONE_CLOUD_PROVIDER = "aws"
PINECONE_CLOUD_REGION = "us-east-1"
PINECONE_INDEX_METRIC = "cosine"
PINECONE_INDEX_NAME = "koi-pond-dev" if DEV else "koi-pond"
PINECONE_BATCH_SIZE = 64
EMBEDDINGS_DIMENSION = 1024
EMBEDDING_QUEUE_LIMIT = 128

VOYAGEAI_API_KEY = os.getenv["VOYAGE_API_KEY"]
VOYAGEAI_MODEL = "voyage-2"
VOYAGEAI_BATCH_SIZE = 128

CHUNK_SIZE = 512
CHUNK_OVERLAP = 80

PUBPUB_USERNAME = os.getenv["PUBPUB_USERNAME"]
PUBPUB_PASSWORD = os.getenv["PUBPUB_PASSWORD"]