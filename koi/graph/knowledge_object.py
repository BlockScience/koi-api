from rid_lib.core import RID
from neo4j import ManagedTransaction

from . import driver


class GraphKnowledgeObject:
    def __init__(self, rid: RID):
        self.rid = rid
    
    @driver.execute_write
    def create(self, tx: ManagedTransaction):
        print("in function")
        print(self, tx)

        labels = f"{self.rid.space}:{self.rid.format}"

        CREATE_OBJECT = f"""//cypher
            MERGE (object:{labels} {{rid: $rid}})
            SET object += $params
            RETURN object
            """

        tx.run(CREATE_OBJECT, rid=str(self.rid), params=self.rid.params)

    @driver.execute_read
    def read_link(self, tx: ManagedTransaction, tag: str):
        READ_OBJECT_LINK = """//cypher
            MATCH (object {rid: $rid})-[:LINK {tag: $tag}]->(target)
            RETURN target.rid AS target
            """
        
        record = tx.run(READ_OBJECT_LINK, rid=str(self.rid), tag=tag).single()

        if record:
            target_rid = record.get("target", None)
            return RID.from_string(target_rid)
        
    @driver.execute_write
    def delete(self, tx: ManagedTransaction):
        DELETE_OBJECT = """//cypher
            MATCH (object {rid: $rid})
            DETACH DELETE object
            RETURN object
            """
        
        record = tx.run(DELETE_OBJECT, rid=str(self.rid)).single()
        return record is not None