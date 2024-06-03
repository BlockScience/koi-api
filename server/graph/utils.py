from .driver import neo4j_driver
from ..config import NEO4J_DB
import functools

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