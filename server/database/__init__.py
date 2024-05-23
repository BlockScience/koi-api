from neo4j import GraphDatabase, exceptions
from server.config import (
    NEO4J_URI,
    NEO4J_AUTH
)

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

try:
    neo4j_driver.verify_connectivity()
except exceptions.ServiceUnavailable:
    print("Failed to connect to Neo4j server")
    quit()