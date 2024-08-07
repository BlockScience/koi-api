import os, json, time, shutil

from rid_lib.core import RID, DataObject

from koi.config import CACHE_DIRECTORY
from koi import utils
from .object_model import CacheObject


class CacheInterface:
    """Interface to the cache of an RID object.
    
    A CacheInterface is automatically generated and bound to all RID 
    objects as the 'cache' property (see extensions.py). It provides
    access to functions viewing and modifying an RID's cache entry.
    
    Example:
        import koi
        from rid_lib.core import RID, DataObject

        rid = RID.from_string("example.rid:string")
        data_object = DataObject(json_data={
            "text": "hello world"
        })
        rid.cache.write(data_object)
        print(rid.cache.read().json())

    Each RID can have a cache file, by default located in the 'cache/' 
    directory, where the filename is the base64 encoding of the RID 
    string + '.json'. Metadata is automatically generated when 'write'
    is called.
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

    def write(
            self, 
            data_object: DataObject | None = None,
            from_dereference: bool = False
        ) -> CacheObject:
        """Writes a DataObject to RID cache.

        If inputted DataObject has JSON data, it is written to the cache
        directory (default 'cache/') as a JSON file with the name set to
        the base 64 encoding of the RID string.

        If inputted DataObject has files, they are written to a
        directory named with the encoded RID string (see above).

        Returns a CacheObject.
        """

        if not os.path.exists(CACHE_DIRECTORY):
            os.makedirs(CACHE_DIRECTORY)

        if (data_object is not None and from_dereference is True) or \
            (data_object is None and from_dereference is False):

            raise Exception(
                "Call to cache write must pass in DataObject OR set "
                "from_dereference = True")

        if from_dereference:
            data_object = self.rid.dereference()

        if not data_object:
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

        metadata = utils.generate_metadata(self.rid, data_object)
        cache_entry = CacheObject(
            metadata=metadata,
            json_data=data_object.json_data
        )

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
        """Reads and return file from RID cache."""
        try:
            with open(f"{self.directory_path}/{file_name}", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete(self):
        """Deletes RID cache entry and associated files."""
        try:
            os.remove(self.file_path)
            shutil.rmtree(self.directory_path)
        except FileNotFoundError:
            return

    @staticmethod
    def drop():
        """Deletes all RID cache entries."""
        try:
            shutil.rmtree(CACHE_DIRECTORY)
        except FileNotFoundError:
            return