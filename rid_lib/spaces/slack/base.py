import slack_bolt

from ... import RID
from ...config import (
    SLACK_BOT_TOKEN,
    SLACK_SIGNING_SECRET
)

class SlackSpace(RID):
    space = "slack"
    app = None

    _domain_workspace_table = {
        "metagov": "TMQ3PKXT9",
        "blockscienceteam": "TA2E6KPK3"
    }

    default_domain = "metagov"

    def __init__(self):
        if not SlackSpace.app:
            SlackSpace.app = slack_bolt.App(
                token=SLACK_BOT_TOKEN,
                signing_secret=SLACK_SIGNING_SECRET
            )

