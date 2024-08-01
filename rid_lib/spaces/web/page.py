import requests
from html2text import html2text

from rid_lib.core import RID, DataObject
from .base import WebSpace


class WebPage(WebSpace):
    format = "page"

    def __init__(self, url: str):
        self.url = url
        self.reference = url
    
    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self) -> DataObject:
        resp = requests.get(self.url)
        content_type = resp.headers.get("Content-Type")
        mime_type = content_type.split(";")[0].strip() if content_type else None

        data = {
            "mime_type": mime_type,
            "text": resp.text
        }

        if "text/html" in content_type:
            data["html"] = resp.text
            data["text"] = html2text(resp.text, bodywidth=0)
        elif "application/json" in content_type:
            data["json"] = resp.json()

        return DataObject(data)

RID._add_type(WebPage)