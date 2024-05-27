from rid_lib import RID
from server import cache

obj = RID.from_string("slack+message:metagov/C06DMGNV7E0/p1713203555733439")

cache.write_rid(obj, {
    "text": "I've just made the RID repository that's going to powering KOI's knowledge base public, thought I'd share it here in case anyone is interested in checking it out. I wrote up some documentation in the readme that will hopefully explain some of the RID concepts a little more clearly! https://github.com/BlockScience/kms-identity"
})