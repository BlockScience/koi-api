from ..base import SlackSpace

class SlackWorkspace(SlackSpace):
    format="workspace"

    _fields_to_save = [
        "id", "name", "url", "domain"
    ]

    def __init__(self, workspace_id: str):
        super().__init__()

        self.workspace_id = workspace_id
        self.reference = workspace_id

    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        response = self.app.client.team_info(
            team=self.workspace_id
        )
        workspace = response["team"]

        data = {
            key: workspace[key] 
            for key in self._fields_to_save
        }
        return data