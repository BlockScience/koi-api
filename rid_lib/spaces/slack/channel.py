from urllib.parse import urlparse

from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import SlackSpace


class SlackChannel(SlackSpace):
    format = "channel"

    @property
    def url(self):
        return f"https://{self.default_domain}.slack.com/archives/{self.channel_id}"
    
    def __init__(self, workspace_id: str, channel_id: str):
        self.workspace_id = workspace_id
        self.channel_id = channel_id

        self.reference = f"{self.workspace_id}/{self.channel_id}"

    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        raise InvalidReferenceFormatError(
            f"SlackChannel RIDs must be in the following format: "
            "'slack.channel:<workspace_id>/<channel_id>'"
        )
        
    @classmethod
    def from_url(cls, slack_url):
        parsed_url = urlparse(slack_url)
        domain = parsed_url.netloc.split(".")[0]
        _, _, channel_id = parsed_url.path.split("/")
        workspace_id = cls._domain_workspace_table.get(domain)

        if not workspace_id:
            raise Exception(
                f"SlackChannel cannot be created from url, domain '{domain}' "
                "not found in domain workspace table")
        
        return cls(workspace_id, channel_id)
        
    def dereference(self):
        channel_data = self.app.client.conversations_info(
            channel=self.channel_id)["channel"]
        return DataObject(
            json_data=channel_data
        )

RID._add_type(SlackChannel)