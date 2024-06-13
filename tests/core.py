import requests

BASE_URL = "http://127.0.0.1:8000/"

OBJECT = "object"
SET = "set"
LINK = "link"

CREATE = "POST"
READ = "GET"
UPDATE = "PUT"
DELETE = "DELETE"

def make_request(method, endpoint, **params):
    response = requests.request(method, BASE_URL + endpoint, json=params)

    data = response.json()

    if response.status_code != 200:
        print("error:")
        for k, v in data.items():
            print(f"\t{k}: {v}")
        response.raise_for_status()


    print(method, "->", endpoint)
    print("input:")
    for k, v in params.items():
        print(f"\t{k}: {v}")
    print("output:")
    if type(data) is dict:
        for k, v in data.items():
            print(f"\t{k}: {v}")
    else:
        print(data)
    print()

    return data
    