import requests

from rid_lib.core import RID
from rid_lib.config import DISCORD_BOT_TOKEN

class DiscordSpace(RID):
    space = "discord"
    
    base_url = "https://discord.com/api/v10"
    
    def authorized_request(self, url, data=None, method="GET"):
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}"
        }
        
        response = requests.request(method, url, data=data, headers=headers)
        return response
    
    