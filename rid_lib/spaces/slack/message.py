from urllib.parse import urlparse, parse_qs

from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import SlackSpace


class SlackMessage(SlackSpace):
    # reference formats: 
    # <workspace_id>/<channel_id>/<message_id>
    # <workspace_id>/<channel_id>/<message_id>/<thread_id>

    format = "message"

    @property
    def url(self):
        url_message_id = "p" + self.message_id.replace(".", "")
        url = f"https://{self.default_domain}.slack.com/archives/{self.channel_id}/{url_message_id}"
        if self.thread_id:
            url += f"?thread_ts={self.thread_id}&cid={self.channel_id}"
        return url

    def __init__(
            self,
            workspace_id: str,
            channel_id: str,
            message_id: str,
            thread_id: str | None = None
        ):
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
        else:
            raise InvalidReferenceFormatError(
                "SlackMessage RIDs must be in one of the following formats: "
                "'slack.message:<workspace_id>/<channel_id>/<message_id>', "
                "'slack.message:<workspace_id>/<channel_id>/<message_id>/<thread_id>'")
        
    # need a better way of getting workspace_id from domain
    @classmethod
    def from_url(cls, slack_url):
        parsed_url = urlparse(slack_url)

        domain = parsed_url.netloc.split(".")[0]
        _, _, channel_id, url_message_id = parsed_url.path.split("/")
        message_id = url_message_id[1:-6] + "." + url_message_id[-6:]
        workspace_id = cls._domain_workspace_table.get(domain)

        params = parse_qs(parsed_url.query)
        if "thread_ts" in params:
            thread_id = params["thread_ts"][0]
        else:
            thread_id = None

        if not workspace_id:
            raise Exception(
                f"SlackMessage cannot be created from url, domain '{domain}' "
                "not found in domain workspace table")
        
        return cls(workspace_id, channel_id, message_id, thread_id)

    def dereference(self):
        if self.is_in_thread:
            response = self.app.client.conversations_replies(
                channel=self.channel_id,
                ts=self.message_id
            )
            message_data = response["messages"][0]
        else:
            response = self.app.client.conversations_history(
                channel=self.channel_id,
                oldest=self.message_id,
                inclusive=True,
                limit=1
            )
            message_data = response["messages"][0]
            
        return DataObject(
            json_data=message_data
        )

RID._add_type(SlackMessage)