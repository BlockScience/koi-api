from .utils import execute_read, execute_write
from rid_lib import RID

@execute_write
def create(tx, rid: RID, members):
    CREATE_SET = """
        MERGE (s:set {rid: $rid})
        SET s += $params
        WITH s UNWIND $member_rids AS member_rid
        MATCH (member {rid: member_rid})
        MERGE (s)-[:CONTAINS]->(member)
        RETURN member.rid
        """
    
    member_records = tx.run(CREATE_SET, rid=str(rid), member_rids=members, params=rid.params)
    members = [record["member.rid"] for record in member_records]

    return members

@execute_read
def read(tx, rid: RID):
    READ_SET = """
        MATCH (s:set {rid: $rid})
        OPTIONAL MATCH (s)-[:CONTAINS]->(member)
        RETURN s.rid, collect(member.rid) AS members
        """
    
    record = tx.run(READ_SET, rid=str(rid)).single()
    if record:
        return record["members"]

@execute_write
def update(tx, rid: RID, add_members, remove_members):
    added_members = []
    removed_members = []

    CHECK_EXISTENCE = """
        MATCH (s:set {rid: $rid})
        RETURN s
        """
    
    result = tx.run(CHECK_EXISTENCE, rid=str(rid))
    if result.peek() is None:
        return None

    if add_members:
        ADD_MEMBERS = """
            MATCH (s:set {rid: $rid})
            UNWIND $member_rids AS member_rid  
            MATCH (member {rid: member_rid})  
            MERGE (s)-[:CONTAINS]->(member)
            RETURN member.rid
            """
        
        added_member_records = tx.run(ADD_MEMBERS, rid=str(rid), member_rids=add_members)
        added_members = [record["member.rid"] for record in added_member_records]
    
    if remove_members:
        REMOVE_MEMBERS = """
            MATCH (s:set {rid: $rid})
            UNWIND $member_rids AS member_rid
            MATCH (s)-[edge:CONTAINS]->(member {rid: member_rid})
            DELETE edge
            RETURN member.rid
            """
        
        removed_member_records = tx.run(REMOVE_MEMBERS, rid=str(rid), member_rids=remove_members)
        removed_members = [record["member.rid"] for record in removed_member_records]

    return added_members, removed_members

@execute_write
def delete(tx, rid: RID):
    DELETE_SET = """
        MATCH (s:set {rid: $rid})
        DETACH DELETE s
        RETURN s
        """
    
    record = tx.run(DELETE_SET, rid=str(rid)).single()
    return bool(record)