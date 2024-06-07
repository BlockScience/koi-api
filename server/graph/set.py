from .utils import execute_read, execute_write
from rid_lib import RID

@execute_write
def create(tx, rid: RID, members):
    CREATE_SET = """
        MERGE (r:set {rid: $rid}) 
        WITH r UNWIND $member_rids AS member_rid
        MATCH (member {rid: member_rid})
        MERGE (r)-[:HAS]->(member)
        RETURN member.rid AS member
        """
    
    member_records = tx.run(CREATE_SET, rid=str(rid), member_rids=members)
    members = [record.get("member") for record in member_records]

    return members



@execute_read
def read(tx, rid: RID):
    READ_SET_MEMBERS = """
        MATCH (r:set {rid: $rid})-[:HAS]->(member)
        RETURN member.rid AS member
        """
    
    member_records = tx.run(READ_SET_MEMBERS, rid=str(rid))
    members = [record.get("member") for record in member_records]

    return members

@execute_write
def update(tx, rid: RID, add_members, remove_members):
    if add_members:
        ADD_MEMBERS = """
            MATCH (r:set {rid: $rid})
            UNWIND $member_rids AS member_rid  
            MATCH (member {rid: member_rid})  
            MERGE (r)-[:HAS]->(member)  
            """
        
        tx.run(ADD_MEMBERS, rid=str(rid), member_rids=add_members)
    
    if remove_members:
        REMOVE_MEMBERS = """
            MATCH (r:set {rid: $rid})
            UNWIND $member_rids AS member_rid
            MATCH (r)-[edge:HAS]->(member {rid: member_rid})
            DELETE edge
            """
        
        tx.run(REMOVE_MEMBERS, rid=str(rid), member_rids=remove_members)