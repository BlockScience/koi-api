import requests

base_url = "http://127.0.0.1:8000/"

conversation_id = requests.post(base_url + "llm").json()["conversation_id"]

while True:
    query = input("User: ")
    response = requests.post(base_url + "llm/" + conversation_id, json={"query": query}).json()["response"]

    print("\nBot: " + response + "\n")