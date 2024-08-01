import requests
import slack_bolt

from rid_lib.core import RID
from rid_lib.config import (
    SLACK_BOT_TOKEN,
    SLACK_SIGNING_SECRET
)

class SlackSpace(RID):
    space = "slack"
    _app = None

    _domain_workspace_table = {
        "metagov": "TMQ3PKXT9",
        "blockscienceteam": "TA2E6KPK3"
    }

    default_domain = "metagov"

    @property
    def app(self):
        if not SlackSpace._app:
            SlackSpace._app = slack_bolt.App(
                token=SLACK_BOT_TOKEN,
                signing_secret=SLACK_SIGNING_SECRET
            )
        
        return SlackSpace._app

    def authorized_request(self, url, data=None, method="GET"):
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
        }

        response = requests.request(method, url, data=data, headers=headers)
        return response