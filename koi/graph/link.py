from neo4j import ManagedTransaction

from . import driver
from .knowledge_object import GraphKnowledgeObject

class GraphLinkObject(GraphKnowledgeObject):
    def create(self, source, target, tag):
        @driver.execute_write
        def execute_create(tx: ManagedTransaction, source, target, tag):
            CREATE_LINK = """//cypher
                MATCH (source {rid: $source_rid})
                MATCH (target {rid: $target_rid})
                MERGE (source)-[link:LINK {rid: $rid}]->(target)
                SET link += $params
                RETURN link
                """
            
            params = {
                **self.rid.params,
                "tag": tag
            }

            record = tx.run(CREATE_LINK, rid=str(self.rid), params=params, source_rid=str(source), target_rid=str(target)).single()
            return record is not None
        
        return execute_create(source, target, tag)
        
    def read(self):
        @driver.execute_read
        def execute_read(tx: ManagedTransaction):
            READ_LINK = """//cypher
                MATCH (source)-[link:LINK {rid: $rid}]->(target)
                RETURN source.rid, target.rid
                """
            
            record = tx.run(READ_LINK, rid=str(self.rid)).single()

            if record:
                return record["source.rid"], record["target.rid"]
        
        return execute_read()

    def delete(self):
        @driver.execute_write
        def execute_delete(tx: ManagedTransaction):
            DELETE_LINK = """//cypher
                MATCH ()-[link:LINK {rid: $rid}]->()
                DELETE link
                RETURN link
                """
                
            record = tx.run(DELETE_LINK, rid=str(self.rid)).single()
            return record is not None

        return execute_delete()