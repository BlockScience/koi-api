from .utils import execute_read, execute_write

@execute_write
def create(tx, rid):
    CREATE_OBJECT = """
        MERGE (object {rid: $rid})
        SET object += $params
        RETURN object
        """
    
    params = {
        "space": rid.space,
        "format": rid.format,
        "means": rid.means,
        "reference": rid.reference
    }

    tx.run(CREATE_OBJECT, rid=str(rid), params=params)