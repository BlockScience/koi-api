from server.config import CACHE_DIRECTORY
from rid_lib import RID
from base64 import urlsafe_b64encode, urlsafe_b64decode
import json
import hashlib
import os

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

def get_rid_file_path(rid: RID):
    return CACHE_DIRECTORY + "/" + encode_b64(str(rid)) + ".json"

def write(rid: RID, data: dict):
    if not os.path.exists("cache"):
        os.makedirs("cache")

    # caches both json data and hash of data
    file_path = get_rid_file_path(rid)
    
    contents = {
        "rid": str(rid),
        "sha256_hash": hash_json(data),
        "data": data
    }

    with open(file_path, "w") as f:
        json.dump(contents, f, indent=2)

def read(rid: RID):
    file_path = get_rid_file_path(rid)

    try:
        with open(file_path, "r") as f:
            contents = json.load(f)
            return contents["data"], contents["sha256_hash"]
    except FileNotFoundError:
        return None, None

def delete(rid: RID):
    file_path = get_rid_file_path(rid)
    os.remove(file_path)
