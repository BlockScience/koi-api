from rid_lib import RID, SlackMessage, UndirectedRelation
import requests
import json

base_url = "http://127.0.0.1:8000"

slack_msg1 = SlackMessage.from_url("https://metagov.slack.com/archives/C06DMGNV7E0/p1716559559903959")
slack_msg2 = RID.from_string("slack+message:metagov/C06DMGNV7E0/p1713203555733439")

requests.post(base_url + "/object", json={
    "rid": str(slack_msg1)
})

requests.post(base_url + "/object", json={
    "rid": str(slack_msg2)
})

resp = requests.post(base_url + "/relation", json={
    "members": [str(slack_msg1), str(slack_msg2)]
})