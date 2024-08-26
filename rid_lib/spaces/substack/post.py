import requests
from html2text import html2text

from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import SubstackSpace


class SubstackPost(SubstackSpace):
    format = "post"

    def __init__(self, subdomain: str, slug: str):
        self.subdomain = subdomain
        self.slug = slug
        self.url = f"https://{subdomain}.substack.com/p/{slug}"
        self.api_url = f"https://{subdomain}.substack.com/api/v1/posts/{slug}"

        self.reference = f"{subdomain}/{slug}"
    
    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        else:
            raise InvalidReferenceFormatError(
                "SubstackPost RIDs must be in the following format: "
                "'substack.post:<subdomain>/<slug>'")
        
    def dereference(self):
        response = requests.get(self.api_url)
        post_data = response.json()
        post_html: str = post_data["body_html"]
        post_text: str = html2text(post_html, bodywidth=0)
        post_data["text"] = post_text

        return DataObject(
            json_data=post_data,
            files={
                f"{self.slug}.md": post_text,
                f"{self.slug}.html": post_html
            }
        )

RID._add_type(SubstackPost)