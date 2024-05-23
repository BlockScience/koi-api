from rid_lib import RID

class SlackMessage(RID):
    space="slack"
    format="message"

    def dereference(self):
        return "slack message"