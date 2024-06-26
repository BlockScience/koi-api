import os

from dotenv import load_dotenv


load_dotenv()

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "koi-pond")
NEO4J_DB = "neo4j" 

CACHE_DIRECTORY = "cache"

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX_NAME = "koi-pond"
EMBEDDINGS_DIMENSION = 1024

VOYAGEAI_API_KEY = os.environ["VOYAGE_API_KEY"]
VOYAGEAI_MODEL = "voyage-2"
VOYAGEAI_BATCH_SIZE = 128