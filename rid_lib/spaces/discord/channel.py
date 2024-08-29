from rid_lib.core import RID, DataObject
from .base import DiscordSpace


class DiscordChannel(DiscordSpace):
    format = "channel"
    
    def __init__(self, channel_id):
        self.channel_id = channel_id
        
        self.reference = self.channel_id
        
    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        resp = self.authorized_request(
            self.base_url + f"/channels/{self.channel_id}"
        )
        
        return DataObject(
            json_data=resp.json()
        )
        
RID._add_type(DiscordChannel)