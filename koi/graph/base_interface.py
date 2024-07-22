from rid_lib.core import RID
from neo4j import ManagedTransaction

from . import driver


class GraphBaseInterface:
    def __init__(self, rid: RID):
        self.rid = rid
    
    def create(self):
        @driver.execute_write
        def execute_create(tx: ManagedTransaction):
            labels = f"{self.rid.space}:{self.rid.format}"

            CREATE_OBJECT = f"""//cypher
                MERGE (object:{labels} {{rid: $rid}})
                SET object += $params
                RETURN object
                """

            tx.run(CREATE_OBJECT, rid=str(self.rid), params=self.rid.params)

        return execute_create()

    def read_link(self, tag: str) -> RID | None:
        @driver.execute_read
        def execute_read_link(tx: ManagedTransaction, tag: str):
            READ_OBJECT_LINK = """//cypher
                MATCH (object {rid: $rid})-[:LINK {tag: $tag}]->(target)
                RETURN target.rid AS target
                """
            
            record = tx.run(READ_OBJECT_LINK, rid=str(self.rid), tag=tag).single()

            if record:
                target_rid = record.get("target", None)
                return RID.from_string(target_rid)
            
        return execute_read_link(tag)
        
    def delete(self):
        @driver.execute_write
        def execute_delete(tx: ManagedTransaction):
            DELETE_OBJECT = """//cypher
                MATCH (object {rid: $rid})
                DETACH DELETE object
                RETURN object
                """
            
            record = tx.run(DELETE_OBJECT, rid=str(self.rid)).single()
            return record is not None
        
        return execute_delete()
    
    @staticmethod
    def drop():
        @driver.execute_write
        def execute_drop(tx: ManagedTransaction):
            DROP_DATABASE = """//cypher
                MATCH (n) DETACH DELETE n
                """
            
            record = tx.run(DROP_DATABASE)
        
        return execute_drop()