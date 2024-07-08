from neo4j import ManagedTransaction

from . import driver
from .knowledge_object import GraphKnowledgeObject

class GraphLinkObject(GraphKnowledgeObject):
    @driver.execute_write
    def create(self, tx: ManagedTransaction, source, target, tag):
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
        
    @driver.execute_read
    def read(self, tx: ManagedTransaction):
        READ_LINK = """//cypher
            MATCH (source)-[link:LINK {rid: $rid}]->(target)
            RETURN source.rid, target.rid
            """
        
        record = tx.run(READ_LINK, rid=str(self.rid)).single()

        if record:
            return record["source.rid"], record["target.rid"]

    @driver.execute_write
    def delete(self, tx: ManagedTransaction):
        DELETE_LINK = """//cypher
            MATCH ()-[link:LINK {rid: $rid}]->()
            DELETE link
            RETURN link
            """
            
        record = tx.run(DELETE_LINK, rid=str(self.rid)).single()
        return record is not None