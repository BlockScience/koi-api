from rid_lib import RID

from .utils import execute_write, execute_read


@execute_write
def create(tx, rid: RID):
    labels = f"{rid.space}:{rid.format}"

    CREATE_OBJECT = f"""
        MERGE (object:{labels} {{rid: $rid}})
        SET object += $params
        RETURN object
        """

    tx.run(CREATE_OBJECT, rid=str(rid), params=rid.params)

@execute_read
def read_link(tx, rid: RID, tag: str):
    READ_OBJECT_LINK = """
        MATCH (object {rid: $rid})-[:LINK {tag: $tag}]->(target)
        RETURN target.rid AS target
        """
    
    record = tx.run(READ_OBJECT_LINK, rid=str(rid), tag=tag).single()

    if record:
        target_rid = record.get("target", None)
        return RID.from_string(target_rid)
    
@execute_write
def delete(tx, rid: RID):
    DELETE_OBJECT = """
        MATCH (object {rid: $rid})
        DETACH DELETE object
        RETURN object
        """
    
    record = tx.run(DELETE_OBJECT, rid=str(rid)).single()
    return record is not None