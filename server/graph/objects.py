from .utils import execute_read, execute_write

@execute_write
def create(tx, rid):
    labels = f"{rid.space}:{rid.format}"

    CREATE_OBJECT = f"""
        MERGE (object:{labels} {{rid: $rid}})
        SET object += $params
        RETURN object
        """
    
    print(CREATE_OBJECT)
    
    params = {
        "space": rid.space,
        "format": rid.format,
        "means": rid.means,
        "reference": rid.reference
    }

    tx.run(CREATE_OBJECT, rid=str(rid), params=params)

@execute_write
def delete(tx, rid):
    DELETE_OBJECT = """
        MATCH (object {rid: $rid})
        DETACH DELETE object
        """
    
    tx.run(DELETE_OBJECT, rid=str(rid))