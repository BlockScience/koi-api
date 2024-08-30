from rid_lib.core import RID, DataObject
from .base import DiscordSpace


class DiscordUser(DiscordSpace):
    format = "user"
    
    def __init__(self, user_id):
        self.user_id = user_id
        
        self.reference = user_id
        
    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        resp = self.authorized_request(
            self.base_url + f"/users/{self.user_id}"
        )
        
        return DataObject(
            json_data=resp.json()
        )
        
RID._add_type(DiscordUser)