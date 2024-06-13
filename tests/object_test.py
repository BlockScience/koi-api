from .core import *

slack_messages = [
    "slack.message:TMQ3PKXT9/C06DMGNV7E0/p1718160412110899",
    "slack.message:TMQ3PKXT9/C06DMGNV7E0/p1717583141346729",
    "slack.message:TMQ3PKXT9/C06DMGNV7E0/p1715260020585939",
    "slack.message:TMQ3PKXT9/C06DMGNV7E0/p1713902180403219"
]

for msg in slack_messages:
    resp = make_request(CREATE, OBJECT, rid=msg, data={}, overwrite=True)

for msg in slack_messages:
    resp = make_request(READ, OBJECT, rid=msg)

resp = make_request(CREATE, SET, members=slack_messages[1:])
set_rid = resp["rid"]

resp = make_request(UPDATE, SET, rid=set_rid, add_members=slack_messages[0:1])

resp = make_request(READ, SET, rid=set_rid)

slack_channel = "slack.channel:TMQ3PKXT9/C06DMGNV7E0"
make_request(CREATE, OBJECT, rid=slack_channel)

make_request(CREATE, LINK, source=slack_channel, target=set_rid, tag="has_messages")

# input()
# make_request(DELETE, SET, rid=set_rid)