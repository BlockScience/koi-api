import json
import hashlib
import slack_bolt
from dotenv import load_dotenv
import os

load_dotenv()

slack_app = slack_bolt.App(
    token=os.environ["SLACK_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)
slack_client = slack_app.client

def hash_json(data: dict):
    # converting dict to string in a repeatable way
    json_string = json.dumps(data, sort_keys=True)
    json_bytes = json_string.encode()

    hash = hashlib.sha256()
    hash.update(json_bytes)
    return hash.hexdigest()