from neo4j import ManagedTransaction
from rid_lib.core import RID

from . import driver
from .base_interface import GraphBaseInterface


class GraphSetInterface(GraphBaseInterface):
    def create(self, members):
        @driver.execute_write
        def execute_create(tx: ManagedTransaction, members):
            CREATE_SET = """//cypher
                MERGE (s:set {rid: $rid})
                SET s += $params
                WITH s UNWIND $member_rids AS member_rid
                MATCH (member {rid: member_rid})
                MERGE (s)-[:CONTAINS]->(member)
                RETURN member.rid
                """
            
            member_records = tx.run(
                CREATE_SET, 
                rid=str(self.rid), 
                member_rids=members, 
                params=self.rid.params
            )

            members = [record["member.rid"] for record in member_records]
            return members
        
        return execute_create(members)

    def read(self):
        @driver.execute_read
        def execute_read(tx: ManagedTransaction):
            READ_SET = """//cypher
                MATCH (s:set {rid: $rid})
                OPTIONAL MATCH (s)-[:CONTAINS]->(member)
                RETURN s.rid, collect(member.rid) AS members
                """
            
            record = tx.run(READ_SET, rid=str(self.rid)).single()
            if record:
                return [RID.from_string(member) for member in record["members"]]
        return execute_read()

    def update(self, add_members=[], remove_members=[]):
        @driver.execute_write
        def execute_update(tx: ManagedTransaction, add_members, remove_members):
            added_members = []
            removed_members = []

            CHECK_EXISTENCE = """//cypher
                MATCH (s:set {rid: $rid})
                RETURN s
                """
            
            result = tx.run(CHECK_EXISTENCE, rid=str(self.rid))
            if result.peek() is None:
                return None

            if add_members:
                ADD_MEMBERS = """//cypher
                    MATCH (s:set {rid: $rid})
                    UNWIND $member_rids AS member_rid  
                    MATCH (member {rid: member_rid})  
                    MERGE (s)-[:CONTAINS]->(member)
                    RETURN member.rid
                    """
                
                added_member_records = tx.run(
                    ADD_MEMBERS, 
                    rid=str(self.rid), 
                    member_rids=add_members
                )
                
                added_members = [
                    record["member.rid"] 
                    for record in added_member_records
                ]
            
            if remove_members:
                REMOVE_MEMBERS = """//cypher
                    MATCH (s:set {rid: $rid})
                    UNWIND $member_rids AS member_rid
                    MATCH (s)-[edge:CONTAINS]->(member {rid: member_rid})
                    DELETE edge
                    RETURN member.rid
                    """
                
                removed_member_records = tx.run(
                    REMOVE_MEMBERS, 
                    rid=str(self.rid), 
                    member_rids=remove_members
                )
                
                removed_members = [
                    record["member.rid"] 
                    for record in removed_member_records
                ]

            return added_members, removed_members
        return execute_update(add_members, remove_members)