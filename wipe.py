from koi.graph import GraphBaseInterface
from koi.cache import CacheInterface
from koi.vectorstore import VectorInterface

GraphBaseInterface.drop()
CacheInterface.drop()
VectorInterface.drop()