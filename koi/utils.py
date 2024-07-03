import json
import hashlib
from base64 import urlsafe_b64encode, urlsafe_b64decode


def encode_b64(string: str):
    encoded_bytes = urlsafe_b64encode(string.encode())
    encoded_string = encoded_bytes.decode()
    # removing base 64 padding
    cleaned_string = encoded_string.rstrip("=")
    return cleaned_string

def decode_b64(string: str):
    # adding padding back in
    padded_string = string + "=" * (-len(string) % 4)
    decoded_bytes = urlsafe_b64decode(padded_string.encode())
    decoded_string = decoded_bytes.decode()
    return decoded_string

def hash_json(data: dict):
    # converting dict to string in a repeatable way
    json_string = json.dumps(data, sort_keys=True)
    json_bytes = json_string.encode()

    hash = hashlib.sha256()
    hash.update(json_bytes)
    return hash.hexdigest()