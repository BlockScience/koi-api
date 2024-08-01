from rid_lib.core import RID, DataObject
from .base import SlackSpace

class SlackWorkspace(SlackSpace):
    format = "workspace"

    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.reference = workspace_id

    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        workspace_data = self.app.client.team_info(team=self.workspace_id)["team"]
        return DataObject(
            json_data=workspace_data
        )
    
RID._add_type(SlackWorkspace)