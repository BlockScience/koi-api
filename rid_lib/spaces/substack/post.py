import requests
from html2text import html2text

from rid_lib.core import RID
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import SubstackSpace


class SubspacePost(SubstackSpace):
    format = "post"

    def __init__(self, subdomain: str, slug: str):
        self.subdomain = subdomain
        self.slug = slug

        self.reference = f"{subdomain}/{slug}"
    
    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        else:
            raise InvalidReferenceFormatError("SubspacePost RIDs must be in the following format: 'substack.post:<subdomain>/<slug>'")
        
    def dereference(self):
        url = f"https://{self.subdomain}.substack.com/api/v1/posts/{self.slug}"
        post_data = requests.get(url).json()
        post_text = html2text(post_data["body_html"], bodywidth=0)
        post_data["text"] = post_text

        return post_data
        
RID._add_type(SubspacePost)