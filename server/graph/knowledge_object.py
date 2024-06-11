from .utils import execute_write, execute_read
from rid_lib import RID

@execute_write
def create(tx, rid):
    labels = f"{rid.space}:{rid.format}"

    CREATE_OBJECT = f"""
        MERGE (object:{labels} {{rid: $rid}})SET object += $params
        RETURN object
        """

    tx.run(CREATE_OBJECT, rid=str(rid), params=rid.params)

@execute_read
def read_link(tx, rid, tag):
    READ_OBJECT_LINK = """
        MATCH (object {rid: $rid})-[:LINK {tag: $tag}]->(target:set)
        RETURN target.rid AS target
        """
    
    record = tx.run(READ_OBJECT_LINK, rid=str(rid), tag=tag).single()

    if record:
        target_rid = record.get("target", None)
        return RID.from_string(target_rid)
    