import json
import hashlib
import time
from base64 import urlsafe_b64encode, urlsafe_b64decode

from rid_lib.core import RID, DataObject


def encode_b64(string: str):
    encoded_bytes = urlsafe_b64encode(string.encode())
    encoded_string = encoded_bytes.decode()
    # removing base 64 padding
    cleaned_string = encoded_string.rstrip("=")
    return cleaned_string

def decode_b64(string: str):
    # adding padding back in
    padded_string = string + "=" * (-len(string) % 4)
    decoded_bytes = urlsafe_b64decode(padded_string.encode())
    decoded_string = decoded_bytes.decode()
    return decoded_string

def hash_json(data: dict):
    # converting dict to string in a repeatable way
    json_string = json.dumps(data, sort_keys=True)
    json_bytes = json_string.encode()

    hash = hashlib.sha256()
    hash.update(json_bytes)
    return hash.hexdigest()

def generate_metadata(rid: RID, data_object: DataObject):
    metadata = {
        "rid": str(rid),
        "space": rid.space,
        "format": rid.format,
        "timestamp": time.time(),
        "sha256_hash": hash_json(
            data_object.json_data or {}
        ),
        "files": list(data_object.files.keys()) if data_object.files else []
    }

    if "text" in data_object.json_data:
        metadata["character_length"] = len(data_object.json_data["text"])
    
    return metadata