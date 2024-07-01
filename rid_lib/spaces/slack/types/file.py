from rid_lib.core import RID
from rid_lib.exceptions import InvalidReferenceFormatError
from ..base import SlackSpace


class SlackFile(SlackSpace):
    # <workspace_id>/<file_id>/<file_name>

    format = "file"

    @property
    def url(self):
        return f"https://files.slack.com/files-pri/{self.workspace_id}-{self.file_id}/{self.file_name}"
    
    def __init__(self, workspace_id: str, file_id: str):
        super().__init__()

        self.workspace_id = workspace_id
        self.file_id = file_id

        self.reference = f"{self.workspace_id}/{self.file_id}"
    
    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        raise InvalidReferenceFormatError(f"SlackFile RIDs must be in the following format: 'slack.file:<workspace_id>/<file_id>'")
    
    def dereference(self):
        file_data = self.app.client.files_info(
            file=self.file_id
        )["file"]
        return file_data

RID._add_type(SlackFile)