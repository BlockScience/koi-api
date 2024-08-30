from urllib.parse import urlparse

from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import DiscordSpace


class DiscordMessage(DiscordSpace):
    format = "message"
    
    # https://discord.com/channels/845050172501262337/928767946040414289/1199916108082327562
    # https://discord.com/channels/845050172501262337/1199916108082327562/1278811819632492544
    
    
    # should guild id be included if its not required by the API?
    def __init__(
        self,
        channel_id: str,
        message_id: str
    ):
        self.channel_id = channel_id
        self.message_id = message_id
        
        self.reference = f"{self.channel_id}/{self.message_id}"
        
    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        else:
            raise InvalidReferenceFormatError(
                "DiscordMessage RID must be in the following format: "
                "'discord.message:<channel_id>/<message_id>'")
            
    @classmethod
    def from_url(cls, discord_url):
        parsed_url = urlparse(discord_url)
        guild_id, channel_id, message_id = parsed_url.path.split("/")[2:]
        
        return cls(channel_id, message_id)
    
    def dereference(self):
        resp = self.authorized_request(
            self.base_url + f"/channels/{self.channel_id}/messages/{self.message_id}"
        )
        
        return DataObject(
            json_data=resp.json()
        )
        
RID._add_type(DiscordMessage)