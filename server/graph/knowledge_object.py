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
def read_link(tx, rid):
    READ_OBJECT_LINK = """
        MATCH (object {rid: $rid})<-[:SOURCE]-(r:link)
        RETURN r.rid AS link
        """
    
    record = tx.run(READ_OBJECT_LINK, rid=str(rid)).single()
    link_rid = record.get("link")

    return RID.from_string(link_rid)
    