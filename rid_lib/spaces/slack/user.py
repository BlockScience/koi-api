from urllib.parse import urlparse

from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import SlackSpace


class SlackUser(SlackSpace):
    format = "user"

    @property
    def url(self):
        return f"https://{self.default_domain}.slack.com/team/{self.user_id}"
    
    def __init__(self, workspace_id: str, user_id: str):
        self.workspace_id = workspace_id
        self.user_id = user_id

        self.reference = f"{self.workspace_id}/{self.user_id}"

    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        else:
            raise InvalidReferenceFormatError(
                f"SlackUser RIDs must be in the following format: "
                "'slack.user:<workspace_id>/<user_id>'")
        
    @classmethod
    def from_url(cls, slack_url):
        parsed_url = urlparse(slack_url)
        domain = parsed_url.netloc.split(".")[0]
        _, _, user_id = parsed_url.path.split("/")
        workspace_id = cls._domain_workspace_table.get(domain)

        if not workspace_id:
            raise Exception(
                f"SlackUser cannot be created from url, domain '{domain}' "
                 "not found in domain workspace table")
        
        return cls(workspace_id, user_id)
    
    def dereference(self):
        profile_data = self.app.client.users_profile_get(user=self.user_id)["profile"]
        user_data = self.app.client.users_info(user=self.user_id)["user"]

        user_data["profile"] = profile_data
        return DataObject(
            json_data=user_data
        )
    
RID._add_type(SlackUser)