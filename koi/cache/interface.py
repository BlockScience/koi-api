import os, json, time, shutil
from typing import Optional

from rid_lib.core import RID, DataObject

from koi.config import CACHE_DIRECTORY
from koi import utils
from .object_model import CacheObject


class CacheInterface:
    """
    Interface to the cache of an RID. A CacheInterface is automatically generated and bound to all RID objects in extensions.py as the 'cache' property. 
    
    For example:
        import koi
        from rid_lib.core import RID, DataObject

        rid = RID.from_string("example.rid:string")
        data_object = DataObject(json_data={
            "test": True
        })
        rid.cache.write(data_object)
        print(rid.cache.read().json())

    Each RID can have a cache file, by default located in the 'cache/' directory, where the filename is the base64 encoding of the RID string + '.json'. Metadata is automatically generate when 'write' is called.
    """

    def __init__(self, rid: RID):
        self.rid = rid
        self.encoded_rid = utils.encode_b64(str(rid))

    @property
    def file_path(self):
        return f"{CACHE_DIRECTORY}/{self.encoded_rid}.json"

    @property
    def directory_path(self):
        return f"{CACHE_DIRECTORY}/{self.encoded_rid}"

    def write(self, data_object: Optional[DataObject] = None, from_dereference: bool = False) -> CacheObject:
        """
        Writes a DataObject to RID cache. Can write both JSON data and files.

        Returns a CacheObject object, which will be empty if nothing was written.
        """

        if not os.path.exists(CACHE_DIRECTORY):
            os.makedirs(CACHE_DIRECTORY)

        if (data_object is not None and from_dereference is True) or \
            (data_object is None and from_dereference is False):

            raise Exception("Call to cache write must pass in DataObject OR set from_dereference = True")

        if from_dereference:
            data_object = self.rid.dereference()

        if not data_object:
            return CacheObject()
        
        if data_object.empty:
            return CacheObject()

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
            "space": self.rid.space,
            "format": self.rid.format,
            "timestamp": time.time(),
            # not currently hashing file data
            "sha256_hash": utils.hash_json(data_object.json_data or {}),
            "files": list(data_object.files.keys()) if data_object.files else []
        }

        if "text" in data_object.json_data:
            metadata["character_length"] = len(data_object.json_data["text"])

        cache_entry = CacheObject(metadata, data_object.json_data)

        with open(self.file_path, "w") as f:
            json.dump(cache_entry.to_dict(), f, indent=2)

        return cache_entry

    def read(self):
        """Reads and returns CacheObject from RID cache."""
        try:
            with open(self.file_path, "r") as f:
                return CacheObject.from_dict(json.load(f))
        except FileNotFoundError:
            return CacheObject()
        
    def read_file(self, file_name):
        try:
            with open(f"{self.directory_path}/{file_name}", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete(self):
        try:
            os.remove(self.file_path)
            shutil.rmtree(self.directory_path)
        except FileNotFoundError:
            return

    @staticmethod
    def drop():
        try:
            shutil.rmtree(CACHE_DIRECTORY)
        except FileNotFoundError:
            return