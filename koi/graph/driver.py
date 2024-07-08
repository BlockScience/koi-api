import functools

from neo4j import GraphDatabase, exceptions

from koi.config import (
    NEO4J_URI,
    NEO4J_AUTH,
    NEO4J_DB
)


neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

try:
    neo4j_driver.verify_connectivity()
except exceptions.ServiceUnavailable:
    print("Failed to connect to Neo4j server")
    quit()


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