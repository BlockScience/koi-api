from .utils import execute_read, execute_write
from rid_lib import RID

@execute_write
def create(tx, rid: RID, members):
    CREATE_UNDIRECTED_RELATION = """
        MERGE (r:set {rid: $rid}) WITH r
        UNWIND $member_rids AS member_rid
        MATCH (member {rid: member_rid})
        CREATE (r)-[:HAS]->(member)
        RETURN COLLECT(member.rid) AS member
        """
    
    member_records = tx.run(CREATE_UNDIRECTED_RELATION, rid=str(rid), member_rids=members)
    members = [record.get("member") for record in member_records]

    return members

@execute_read
def exists(tx, rid: RID):
    READ_UNDIRECTED_RELATION = """
        MATCH (r:set {rid: $rid})
        RETURN r AS relation
        """
    
    relation_record = tx.run(READ_UNDIRECTED_RELATION, rid=str(rid))
    return relation_record.peek() is not None

@execute_read
def read(tx, rid: RID):
    READ_UNDIRECTED_RELATION_MEMBERS = """
        MATCH (r:set {rid: $rid})-[:HAS]->(member)
        RETURN member.rid AS member
        """
    
    member_records = tx.run(READ_UNDIRECTED_RELATION_MEMBERS, rid=str(rid))
    members = [record.get("member") for record in member_records]

    return members

@execute_write
def update(tx, rid: RID, members_to_add, members_to_remove):
    if (not members_to_add) and (not members_to_remove):
        return
    
    if members_to_add:
        ADD_MEMBERS = """
            MATCH (r:set {rid: $rid})
            UNWIND $member_rids AS member_rid  
            MATCH (member {rid: member_rid})  
            MERGE (r)-[:HAS]->(member)  
            """
        
        tx.run(ADD_MEMBERS, rid=str(rid), member_rids=members_to_add)
    
    if members_to_remove:
        REMOVE_MEMBERS = """
            MATCH (r:set {rid: $rid})
            UNWIND $member_rids AS member_rid
            MATCH (r)-[edge:HAS]->(member {rid: member_rid})
            DELETE edge
            """
        
        tx.run(REMOVE_MEMBERS, rid=str(rid), member_rids=members_to_remove)

@execute_write
def delete(tx, rid: RID):
    DELETE_UNDIRECTED_RELATION = """
        MATCH (r:set {rid: $rid})
        DETACH DELETE r
        """
    
    tx.run(DELETE_UNDIRECTED_RELATION, rid=str(rid))