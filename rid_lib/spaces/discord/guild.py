from rid_lib.core import RID, DataObject
from .base import DiscordSpace


class DiscordGuild(DiscordSpace):
    format = "guild"
    
    def __init__(self, guild_id):
        self.guild_id = guild_id
        
        self.reference = guild_id
        
    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        resp = self.authorized_request(
            self.base_url + f"/guilds/{self.guild_id}"
        )
        
        return DataObject(
            json_data=resp.json()
        )
        
RID._add_type(DiscordGuild)