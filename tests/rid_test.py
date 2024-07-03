from rid_lib.spaces.internal import InternalLink
from rid_lib.spaces.slack import *

msg1 = SlackMessage.from_url("https://metagov.slack.com/archives/C06DMGNV7E0/p1718871472001789")
# msg2 = SlackMessage.from_string("slack.message:TMQ3PKXT9/C06DMGNV7E0/1718871472.001789")
msg3 = SlackMessage.from_reference("TMQ3PKXT9/C06DMGNV7E0/1718871472.001789")
msg4 = SlackMessage("TMQ3PKXT9", "C06DMGNV7E0", "1718871472.001789")

print(msg1, msg3, msg4)
print(msg1.dereference())

channel = SlackChannel.from_reference("TMQ3PKXT9/C06DMGNV7E0")
channel2 = SlackChannel("TMQ3PKXT9", "C06DMGNV7E0")
print(channel, channel2)
print(channel.dereference())

workspace = SlackWorkspace("TMQ3PKXT9")
print(workspace)
print(workspace.dereference())

link = InternalLink(msg1, channel, "are_friends")
print(link)
link2 = InternalLink.from_reference("are_friends+5c5280f83d61645fb1539811f2daf0816444114f3e01ba42f45ccffcffba05e9")
print(link2)