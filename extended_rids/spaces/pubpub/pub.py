import requests
from html2text import html2text

from rid_lib.core import RID, DataObject
from rid_lib.exceptions import InvalidReferenceFormatError
from .base import PubPubSpace


class PubPubPub(PubPubSpace):
    format = "pub"

    def __init__(self, subdomain: str, slug: str):
        self.subdomain = subdomain
        self.slug = slug
        self.url = f"https://{subdomain}.pubpub.org/pub/{slug}"

        self.reference = f"{subdomain}/{slug}"

    @classmethod
    def from_reference(cls, reference):
        components = reference.split("/")
        if len(components) == 2:
            return cls(*components)
        else:
            raise InvalidReferenceFormatError(
                "PubPubPub RIDs must be in the following format: "
                "'pubpub.pub:<subdomain>/<slug>'")
        
    def dereference(self) -> DataObject:
        resp = requests.get(self.url)
        pub_text = html2text(resp.text)

        return DataObject(
            json_data={
                "text": pub_text
            }
        )

RID._add_type(PubPubPub)