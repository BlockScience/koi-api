from .utils import execute_read, execute_write
from rid_lib import RID


@execute_read
def exists(tx, rid: RID):
    READ_NODE = """
        MATCH (n {rid: $rid})
        RETURN n
        """
    
    node_record = tx.run(READ_NODE, rid=str(rid))
    return node_record.peek() is not None

@execute_write
def delete(tx, rid: RID):
    DELETE_NODE = """
        MATCH (n {rid: $rid})
        DETACH DELETE n
        """

    tx.run(DELETE_NODE, rid=str(rid))