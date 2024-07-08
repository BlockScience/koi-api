from typing import Optional
import json
import os
import time

from rid_lib.core import RID, DataObject

from .config import CACHE_DIRECTORY
from . import utils


if not os.path.exists(CACHE_DIRECTORY):
    os.makedirs(CACHE_DIRECTORY)

class CacheEntry:
    def __init__(
            self, 
            metadata: Optional[dict] = None,
            json_data: Optional[dict] = None
        ):
        
        self.metadata = metadata
        self.json_data = json_data
        self.files = []

        if self.metadata:
            for file in self.metadata.get("files", []):
                self.files.append(file)
    
    @property
    def empty(self):
        return self.metadata is None and self.json_data is None

    @classmethod
    def from_json(cls, json_object):
        if (json_object is None) or (json_object == {}):
            raise Exception("Invalid JSON body read from cached file")

        return cls(
            json_object.get("metadata"),
            json_object.get("data")
        )

    def json(self):
        return {
            "metadata": self.metadata,
            "data": self.json_data,
        }

class CacheableObject:
    def __init__(self, rid: RID):
        self.rid = rid
        self.encoded_rid = utils.encode_b64(str(rid))

    @property
    def file_path(self):
        return f"{CACHE_DIRECTORY}/{self.encoded_rid}.json"

    @property
    def directory_path(self):
        return f"{CACHE_DIRECTORY}/{self.encoded_rid}"

    def write(self, data_object: Optional[DataObject] = None, from_dereference: bool = False):
        if (data_object is not None and from_dereference is True) or \
            (data_object is None and from_dereference is False):

            raise Exception("Call to cache write must pass in DataObject OR set by_dereference = True")

        if from_dereference:
            data_object = self.rid.dereference()

        if not data_object:
            return
        
        if data_object.empty:
            return

        if data_object.files:
            if not os.path.exists(self.directory_path):
                os.makedirs(self.directory_path)
            
            for file_name, binary_data in data_object.files.items():
                with open(f"{self.directory_path}/{file_name}", "wb") as f:
                    if type(binary_data) is bytes:
                        f.write(binary_data)
                    elif type(binary_data) is str:
                        f.write(binary_data.encode())

        metadata = {
            "rid": str(self.rid),
            "timestamp": time.time(),
            # not currently hashing file data
            "sha256_hash": utils.hash_json(data_object.json_data),
            "files": list(data_object.files.keys()) if data_object.files else []
        }

        cache_entry = CacheEntry(metadata, data_object.json_data)

        with open(self.file_path, "w") as f:
            json.dump(cache_entry.json(), f, indent=2)

        return cache_entry

    def read(self):
        try:
            with open(self.file_path, "r") as f:
                return CacheEntry.from_json(json.load(f))
        except FileNotFoundError:
            return CacheEntry()
        
    def read_file(self, file_name):
        try:
            with open(f"{self.directory_path}/{file_name}", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete(self):
        os.remove(self.file_path)