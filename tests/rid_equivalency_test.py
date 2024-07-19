from rid_lib.types import SlackMessage

msg1_url = SlackMessage.from_url("https://metagov.slack.com/archives/C06LAQNLVNK/p1718185155982379?thread_ts=1718183944.560199&cid=C06LAQNLVNK")
msg1_params = SlackMessage("TMQ3PKXT9", "C06LAQNLVNK", "1718185155.982379", "1718183944.560199")
msg1_ref = SlackMessage.from_reference("TMQ3PKXT9/C06LAQNLVNK/1718185155.982379/1718183944.560199")

print(msg1_url)
print(msg1_params)
print(msg1_ref)
print(msg1_url == msg1_params)
print(msg1_params == msg1_ref)
assert msg1_url == msg1_params
assert msg1_params == msg1_ref
print(msg1_url.dereference())

msg2_url = SlackMessage.from_url("https://metagov.slack.com/archives/C06DMGNV7E0/p1718160412110899")
msg2_params = SlackMessage("TMQ3PKXT9", "C06DMGNV7E0", "1718160412.110899")
msg2_ref = SlackMessage.from_reference("TMQ3PKXT9/C06DMGNV7E0/1718160412.110899")

print(msg2_url)
assert msg2_url == msg2_params
assert msg2_params == msg2_ref
print(msg2_url.dereference())