import functools
import time

from neo4j import GraphDatabase, exceptions

from koi.config import (
    NEO4J_URI,
    NEO4J_AUTH,
    NEO4J_DB
)


neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

timeout = 5
while True:
    try:
        neo4j_driver.verify_connectivity()
        print("Connected to Neo4j server successfully")
        break
    except exceptions.ServiceUnavailable:
        print(f"Failed to connect to Neo4j server, retrying in {timeout} seconds")
        time.sleep(timeout)


# Wrapper functions for performing Neo4j Cypher operations
def execute_read(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with neo4j_driver.session(database=NEO4J_DB) as session:
            return session.execute_read(func, *args, **kwargs)
    return wrapper

def execute_write(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with neo4j_driver.session(database=NEO4J_DB) as session:
            return session.execute_write(func, *args, **kwargs)
    return wrapper