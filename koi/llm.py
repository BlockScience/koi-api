import json

from openai import OpenAI
import nanoid
from rid_lib.core import RID

from .config import OPENAI_API_KEY
from . import vectorstore


client = OpenAI(api_key=OPENAI_API_KEY)

try:
    with open("conversations.json", "r") as f:
        conversations = json.load(f)
except FileNotFoundError:
    conversations = {}

system_prompt = {
    "role": "system", 
    "content": "You are a helpful assistant that is a part of KOI Pond, a Knowledge Organization Infrastructure system, that responds to user queries with the help of KOI's knowledge. A user will ask you questions prefixed by 'User:'. Several knowledge objects will be returned from KOI identified by an id in the following format 'Knowledge Object [{n}] {id}'. Ids will take the following format '{space}.{type}:{reference}'. The number of the reference will be included in square brackets. Use this information in addition to the context of the ongoing conversation to respond to the user. If the information provided is insufficient to answer a question, simply convey that to the user, do not make up an answer that doesn't have any basis. YOU MUST CITE ALL PROVIDED SOURCES DIRECTLY AFTER INFORMATION GENERATED BASED ON THAT SOURCE WITH A NUMBERED REFERENCE IN THE FOLLOWING FORMAT: '[{n}]' where n is a number, for example '[3]'. THE SOURCES ARE ALREADY PROVIDED TO THE USER, DO NOT INCLUDE FOOTNOTES OR REFERENCES AT THE END OF YOUR MESSAGE."
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
    print(rids)
    for n, rid in enumerate(rids):
        cached_object = rid.cache.read()
        if cached_object.data is None:
            cached_object = rid.cache.write(from_dereference=True)
        
        text = cached_object.data["text"]
        knowledge += f"Knowledge Object [{n+1}] {str(rid)}\n{text}\n\n"


    # knowledge += "Footnotes:\n" + footnote_table

    print(knowledge)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation + [{
            "role": "user",
            "content": query + "\n\n" + knowledge
        }]
    )

    # not including knowledge in conversation history, only active query
    conversation.append({
        "role": "user",
        "content": query
    })

    bot_message = response.choices[0].message.content

    footnote_table = ""
    for n, rid in enumerate(rids):
        line = f"{n+1}: <{rid}>"
        if f"[{n+1}]" not in bot_message:
            line = f"~{line}~"
        footnote_table += line + "\n"
    
    conversation.append({
        "role": "assistant",
        "content": bot_message
    })

    with open("conversations.json", "w") as f:
        json.dump(conversations, f, indent=2)

    return bot_message + "\n\n" + footnote_table