from rid_lib import RID

from . import driver


@driver.execute_write
def create(tx, rid: RID, source, target, tag):
    CREATE_LINK = """
        MATCH (source {rid: $source_rid})
        MATCH (target {rid: $target_rid})
        MERGE (source)-[link:LINK {rid: $rid}]->(target)
        SET link += $params
        RETURN link
        """
    
    params = {
        **rid.params,
        "tag": tag
    }

    record = tx.run(CREATE_LINK, rid=str(rid), params=params, source_rid=str(source), target_rid=str(target)).single()
    return record is not None
    
@driver.execute_read
def read(tx, rid: RID):
    READ_LINK = """
        MATCH (source)-[link:LINK {rid: $rid}]->(target)
        RETURN source.rid, target.rid
        """
    
    record = tx.run(READ_LINK, rid=str(rid)).single()

    if record:
        return record["source.rid"], record["target.rid"]

@driver.execute_write
def delete(tx, rid: RID):
    DELETE_LINK = """
        MATCH ()-[link:LINK {rid: $rid}]->()
        DELETE link
        RETURN link
        """
        
    record = tx.run(DELETE_LINK, rid=str(rid)).single()
    return record is not None