from .utils import execute_read, execute_write
from rid_lib import RID

@execute_write
def create(tx, rid: RID, tag, source, target):
    CREATE_LINK = """
        MATCH (source {rid: $source_rid})
        MATCH (target {rid: $target_rid})
        MERGE (source)-[link:LINK {rid: $rid}]->(target)
        SET link += $params
        RETURN link.rid AS link
        """
    
    params = {
        **rid.params,
        "tag": tag
    }

    link = tx.run(CREATE_LINK, rid=str(rid), params=params, source_rid=source, target_rid=target)

    return

@execute_read
def read(tx, rid: RID):
    READ_LINK = """
        MATCH (source)-[link:LINK {rid: $rid}]->(target)
        RETURN source, target
        """
    
    record = tx.run(READ_LINK, rid=str(rid)).single()
    return record["source"]["rid"], record["target"]["rid"]

@execute_write
def delete(tx, rid: RID):
    DELETE_LINK = """
        MATCH ()-[link:LINK {rid: $rid}]->()
        DELETE link
        """
        
    tx.run(DELETE_LINK, rid=str(rid))