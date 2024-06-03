from rid_lib import RID
from urllib.parse import urlparse

class SlackMessage(RID):
    space="slack"
    format="message"

    @classmethod
    def from_url(cls, slack_url):
        parsed_url = urlparse(slack_url)

        workspace = parsed_url.netloc.split(".")[0]
        _, _, channel_id, message_id = parsed_url.path.split("/")

        reference = f"{workspace}/{channel_id}/{message_id}"

        return cls(reference)

    def dereference(self):
        return {
            "text": "slack message"
        }

class UndirectedRelation(RID):
    space="internal"
    format="set"

    def dereference(self):
        pass

class DirectedRelation(RID):
    space="internal"
    format="link"

    def dereference(self):
        pass