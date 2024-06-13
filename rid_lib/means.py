from . import RID, utils
from urllib.parse import urlparse

class SlackMessage(RID):
    space="slack"
    format="message"

    def __init__(self, reference=None):
        super().__init__(reference)

        components = self.reference.split("/")
        self.workspace_id, self.channel_id, self.timestamp = components

    @classmethod
    def from_url(cls, slack_url):
        parsed_url = urlparse(slack_url)

        workspace = parsed_url.netloc.split(".")[0]
        _, _, channel_id, message_id = parsed_url.path.split("/")
        timestamp = message_id[1:-6] + "." + message_id[-6:]

        reference = f"{workspace}/{channel_id}/{timestamp}"

        return cls(reference)

    def dereference(self):
        response = utils.slack_client.conversations_history(
            channel=self.channel_id,
            oldest=self.timestamp,
            inclusive=True,
            limit=1
        )
        return response["messages"][0]
    
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
    def from_params(cls, tag, source, target):
        hashed_link = utils.hash_json({
            "source": source,
            "target": target
        })

        reference = f"{tag}+{hashed_link}"
        return cls(reference)
