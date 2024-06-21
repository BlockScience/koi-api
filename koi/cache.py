from typing import Optional
import json
import hashlib
import os
from base64 import urlsafe_b64encode, urlsafe_b64decode

from rid_lib import RID

from koi.config import CACHE_DIRECTORY


class CacheableObject:
    def __init__(self, rid: RID, data: Optional[dict] = None, metadata: Optional[dict] = None):
        self.rid = rid
        self.data = data
        self.metadata = metadata

    @classmethod
    def from_json(cls, json_object):
        if (json_object is None) or (json_object == {}):
            raise Exception("Invalid JSON body read from cached file")

        return cls(
            RID.from_string(json_object.get("rid")),
            json_object.get("data"),
            json_object.get("metadata")
        )

    def json(self):
        return {
            "rid": str(self.rid),
            "data": self.data,
            "metadata": self.metadata
        }

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
    metadata = {
        "sha256_hash": hash_json(data)
    }

    cached_object = CacheableObject(rid, data, metadata)

    file_path = get_rid_file_path(rid)

    with open(file_path, "w") as f:
        json.dump(cached_object.json(), f, indent=2)

    return cached_object

def read(rid: RID):
    file_path = get_rid_file_path(rid)

    try:
        with open(file_path, "r") as f:
            json_object = json.load(f)
            return CacheableObject.from_json(json_object)
    except FileNotFoundError:
        return CacheableObject(rid)

def delete(rid: RID):
    file_path = get_rid_file_path(rid)
    os.remove(file_path)
