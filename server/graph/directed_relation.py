from .utils import execute_read, execute_write
from rid_lib import RID

@execute_write
def create(tx, rid: RID, sources, targets):
    CREATE_DIRECTED_RELATION = """
        MERGE (r:link {rid: $rid})
        WITH r UNWIND $source_rids AS source_rid
        MATCH (source {rid: source_rid})
        MERGE (r)-[:SOURCE]->(source)
        RETURN COLLECT(source.rid) AS source
        """
    
    source_records = tx.run(CREATE_DIRECTED_RELATION, rid=str(rid), source_rids=sources)
    sources = [record.get("source") for record in source_records]

    ADD_TARGETS = """
        MATCH (r:link {rid: $rid})
        UNWIND $target_rids AS target_rid
        MATCH (target {rid: target_rid})
        MERGE (r)-[:TARGET]->(target)
        RETURN COLLECT(target.rid) AS target
        """
    
    target_records = tx.run(ADD_TARGETS, rid=str(rid), target_rids=targets)
    targets = [record.get("target") for record in target_records]

    return sources, targets

@execute_read
def read(tx, rid: RID):
    READ_DIRECTED_RELATION_MEMBERS = """
        MATCH (r:link {rid: $rid})-[e:SOURCE|TARGET]->(member)
        RETURN TYPE(e) AS type, member.rid AS member
        """
    
    member_records = tx.run(READ_DIRECTED_RELATION_MEMBERS, rid=str(rid))
    sources = []
    targets = []

    for record in member_records:
        edge_type = record.get("type")
        member = record.get("member")

        if edge_type == "SOURCE":
            sources.append(member)
        elif edge_type == "TARGET":
            targets.append(member)
    
    return sources, targets

@execute_write
def update(tx, rid: RID, add_sources, remove_sources, add_targets, remove_targets):
    if add_sources:
        ADD_SOURCES = """
            MATCH (r:link {rid: $rid})
            UNWIND $source_rids AS source_rid
            MATCH (source {rid: source_rid})
            MERGE (r)-[:SOURCE]->(source)
            """

        tx.run(ADD_SOURCES, rid=str(rid), source_rids=add_sources)

    if add_targets:
        ADD_TARGETS = """
            MATCH (r:link {rid: $rid})
            UNWIND $target_rids AS target_rid
            MATCH (target {rid: target_rid})
            MERGE (r)-[:TARGET]->(target)
            """

        tx.run(ADD_TARGETS, rid=str(rid), target_rids=add_targets)
    
    if remove_sources:
        REMOVE_SOURCES = """
            MATCH (r:link {rid: $rid})
            UNWIND $source_rids AS source_rid
            MATCH (r)-[edge:SOURCE]->(source {rid: source_rid})
            DELETE edge
            """
        
        tx.run(REMOVE_SOURCES, rid=str(rid), source_rids=remove_sources)

    if remove_targets:
        REMOVE_TARGETS = """
            MATCH (r:link {rid: $rid})
            UNWIND $target_rids AS target_rid
            MATCH (r)-[edge:TARGET]->(target {rid: target_rid})
            DELETE edge
            """
        
        tx.run(REMOVE_TARGETS, rid=str(rid), target_rids=remove_targets)