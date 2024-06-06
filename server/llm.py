from openai import OpenAI
from .config import OPENAI_API_KEY
from . import vectorstore, cache
from rid_lib import RID

client = OpenAI(api_key=OPENAI_API_KEY)

query = input("> ")

rids = [RID.from_string(rid) for rid, score in vectorstore.query(query)]

knowledge = "" 

for rid in rids:
    print(str(rid))
    data, _ = cache.read(rid)
    text = data["text"]
    knowledge += text + "\n"

# print(knowledge)

print("\nBot response:")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that answers questions informed by a document search system. The system has returned the following data to help you answer the user's query: " + knowledge},
        {"role": "user", "content": query}
    ]
)

print(response.choices[0].message.content)