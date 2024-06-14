from openai import OpenAI
from .config import OPENAI_API_KEY
from . import vectorstore, cache
from rid_lib import RID
import nanoid, json

client = OpenAI(api_key=OPENAI_API_KEY)

try:
    with open("conversations.json", "r") as f:
        conversations = json.load(f)
        print(conversations)
except FileNotFoundError:
    conversations = {}

system_prompt = {
    "role": "system", 
    "content": "You are a helpful assistant that is a part of KOI Pond, a Knowledge Organization Infrastructure system, that responds to user queries with the help of KOI's knowledge. A user will ask you questions prefixed by 'User:'. Several knowledge objects will be returned from KOI identified by an id in the following format 'Knowledge Object <id>:'. Use this information in addition to the context of the ongoing conversation to respond to the user. If the information provided is insufficient to answer a question, simply convey that to the user, do not make up an answer that doesn't have any basis."
}

def start_conversation(conversation_id=None):
    conversation_id = conversation_id or nanoid.generate()
    conversations[conversation_id] = [system_prompt]
    return conversation_id

def continue_conversation(conversation_id, query):
    conversation = conversations.get(conversation_id)
    if conversation is None:
        start_conversation(conversation_id)
    conversation = conversations.get(conversation_id)

    knowledge = ""
    rids = [RID.from_string(rid) for rid, score in vectorstore.query(query)]
    for rid in rids:
        data, _ = cache.read(rid)
        text = data["text"]
        knowledge += f"Knowledge Object {str(rid)}:\n{text}\n\n"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation + [{
            "role": "user",
            "content": f"User: {query}\n\n{knowledge}"
        }]
    )

    # not including knowledge in conversation history, only active query
    conversation.append({
        "role": "user",
        "content": f"User: {query}"
    })

    bot_message = response.choices[0].message.content
    
    conversation.append({
        "role": "assistant",
        "content": bot_message
    })

    with open("conversations.json", "w") as f:
        json.dump(conversations, f, indent=2)

    return bot_message