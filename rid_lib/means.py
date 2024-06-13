from . import RID, utils
from urllib.parse import urlparse, parse_qs
from typing import Optional

class SlackMessage(RID):
    # reference formats: 
    # <workspace_id>/<channel_id>/<message_id>
    # <workspace_id>/<channel_id>/<message_id>/<thread_id>

    space="slack"
    format="message"

    _fields_to_save = [
        "user", "type", "subtype", "text"
    ]

    _domain_workspace_table = {
        "metagov": "TMQ3PKXT9"
    }

    def __init__(self, workspace_id: str, channel_id: str, message_id: str, thread_id: Optional[str] = None):
        self.workspace_id = workspace_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.thread_id = thread_id

        if thread_id:
            self.is_in_thread = True
            self.reference = f"{workspace_id}/{channel_id}/{message_id}/{thread_id}"
        else:
            self.is_in_thread = False
            self.reference = f"{workspace_id}/{channel_id}/{message_id}"

    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) in (3, 4):
            return cls(*components)
        
    
    # need a better way of getting workspace_id from domain
    @classmethod
    def from_url(cls, slack_url):
        parsed_url = urlparse(slack_url)

        domain = parsed_url.netloc.split(".")[0]
        _, _, channel_id, url_message_id = parsed_url.path.split("/")
        message_id = url_message_id[1:-6] + "." + url_message_id[-6:]
        workspace_id = cls._domain_workspace_table.get(domain, None)

        params = parse_qs(parsed_url.query)
        if "thread_ts" in params:
            thread_id = params["thread_ts"][0]
        else:
            thread_id = None

        if not workspace_id:
            raise Exception(f"SlackMessage cannot be created from url, domain '{domain}' not found in domain workspace table")
        
        return cls(workspace_id, channel_id, message_id, thread_id)

    def dereference(self):
        if self.is_in_thread:
            response = utils.slack_client.conversations_replies(
                channel=self.channel_id,
                ts=self.message_id
            )
            message = response["messages"][0]
        else:
            response = utils.slack_client.conversations_history(
                channel=self.channel_id,
                oldest=self.message_id,
                inclusive=True,
                limit=1
            )
            message = response["messages"][0]

        return {
            key: message.get(key, None)
            for key in self._fields_to_save
        }
        

    
class SlackUser(RID):
    space="slack"
    format="user"
    
class SlackChannel(RID):
    space="slack"
    format="channel"

class SlackWorkspace(RID):
    space="slack"
    format="workspace"

class Set(RID):
    space="internal"
    format="set"

class Link(RID):
    space="internal"
    format="link"

    @classmethod
    def from_params(cls, source, target, tag):
        hashed_link = utils.hash_json({
            "source": source,
            "target": target
        })

        reference = f"{tag}+{hashed_link}"
        return cls(reference)
