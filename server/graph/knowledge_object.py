from .utils import execute_write

@execute_write
def create(tx, rid):
    labels = f"{rid.space}:{rid.format}"

    CREATE_OBJECT = f"""
        MERGE (object:{labels} {{rid: $rid}})
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