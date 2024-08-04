from neo4j import ManagedTransaction
from rid_lib.core import RID

from . import driver
from .base_interface import GraphBaseInterface

class GraphLinkInterface(GraphBaseInterface):
    """Interface to graph representation a link RID object.

    (see GraphBaseInterface for default behavior)

    A link is an immutable directed edge between two graph objects, with
    a human readable tag.

        (obj1)-[link]->(obj2)

    """

    def create(self) -> bool:
        """Creates a new link RID graph object."""
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

            record = tx.run(
                CREATE_LINK, 
                rid=str(self.rid), 
                params=params, 
                source_rid=str(source), 
                target_rid=str(target)
            ).single()
            
            return record is not None
        
        return execute_create(self.rid.source, self.rid.target, self.rid.tag)
        
    def read(self) -> tuple[RID, RID] | None:
        """Returns RIDs of linked source and target object."""
        @driver.execute_read
        def execute_read(tx: ManagedTransaction):
            READ_LINK = """//cypher
                MATCH (source)-[link:LINK {rid: $rid}]->(target)
                RETURN source.rid, target.rid
                """
            
            record = tx.run(READ_LINK, rid=str(self.rid)).single()

            if record:
                return (
                    RID.from_string(record["source.rid"]), 
                    RID.from_string(record["target.rid"])
                )
        
        return execute_read()

    def delete(self) -> bool:
        """Deletes link RID graph object."""
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