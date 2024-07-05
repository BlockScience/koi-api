from rid_lib import RID
from rid_lib.types import InternalLink

from . import driver
from .base import GraphObject

class GraphLinkObject(GraphObject):
    @driver.execute_write
    def create(tx, self, source, target, tag):
        CREATE_LINK = """
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
    def read(tx, self):
        READ_LINK = """
            MATCH (source)-[link:LINK {rid: $rid}]->(target)
            RETURN source.rid, target.rid
            """
        
        record = tx.run(READ_LINK, rid=str(self.rid)).single()

        if record:
            return record["source.rid"], record["target.rid"]

    @driver.execute_write
    def delete(tx, self):
        DELETE_LINK = """
            MATCH ()-[link:LINK {rid: $rid}]->()
            DELETE link
            RETURN link
            """
            
        record = tx.run(DELETE_LINK, rid=str(self.rid)).single()
        return record is not None