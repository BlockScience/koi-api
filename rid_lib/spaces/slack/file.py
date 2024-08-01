from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import SlackSpace


class SlackFile(SlackSpace):
    # <workspace_id>/<file_id>/<file_name>

    format = "file"

    @property
    def url(self):
        return ("https://files.slack.com/files-pri/"
                f"{self.workspace_id}-{self.file_id}/{self.file_name}")
    
    def __init__(self, workspace_id: str, file_id: str):
        self.workspace_id = workspace_id
        self.file_id = file_id

        self.reference = f"{self.workspace_id}/{self.file_id}"
    
    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        raise InvalidReferenceFormatError(
            f"SlackFile RIDs must be in the following format: "
            "'slack.file:<workspace_id>/<file_id>'")
    
    def dereference(self):
        file_data = self.app.client.files_info(
            file=self.file_id
        )["file"]

        file_url = file_data["url_private"]
        file_binary = self.authorized_request(file_url).content

        return DataObject(
            json_data=file_data,
            files={
                file_data["name"]: file_binary
            }
        )


RID._add_type(SlackFile)