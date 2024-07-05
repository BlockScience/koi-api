from rid_lib import RID

from . import driver
from .base import GraphObject


class GraphKnowledgeObject(GraphObject):
    @driver.execute_write
    def create(tx, self):
        labels = f"{self.rid.space}:{self.rid.format}"

        CREATE_OBJECT = f"""
            MERGE (object:{labels} {{rid: $rid}})
            SET object += $params
            RETURN object
            """

        tx.run(CREATE_OBJECT, rid=str(self.rid), params=self.rid.params)

    @driver.execute_read
    def read_link(tx, self, tag: str):
        READ_OBJECT_LINK = """
            MATCH (object {rid: $rid})-[:LINK {tag: $tag}]->(target)
            RETURN target.rid AS target
            """
        
        record = tx.run(READ_OBJECT_LINK, rid=str(self.rid), tag=tag).single()

        if record:
            target_rid = record.get("target", None)
            return RID.from_string(target_rid)
        
    @driver.execute_write
    def delete(tx, self):
        DELETE_OBJECT = """
            MATCH (object {rid: $rid})
            DETACH DELETE object
            RETURN object
            """
        
        record = tx.run(DELETE_OBJECT, rid=str(self.rid)).single()
        return record is not None