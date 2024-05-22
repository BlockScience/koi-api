from means import *

if __name__ == "__main__":
    rid = RID.from_string("slack/message:metagov/C06DMGNV7E0/p1713203555733439")

    print(rid.means, rid.space, rid.format, rid.reference)
    print(rid.dereference())