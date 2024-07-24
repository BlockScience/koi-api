import json

from openai import OpenAI
import nanoid

from .config import OPENAI_API_KEY
from .vectorstore import VectorInterface


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
    """Creates a new conversation with provided id, or generates one randomly."""
    conversation_id = conversation_id or nanoid.generate()
    conversations[conversation_id] = [system_prompt]
    return conversation_id

def continue_conversation(conversation_id, query):
    """Continues conversation, returns response."""
    conversation = conversations.get(conversation_id)
    if conversation is None:
        start_conversation(conversation_id)
    conversation = conversations.get(conversation_id)

    vectors = VectorInterface.query(query)
    # removes duplicates in the case of multiple chunks from the same document
    unique_vector_rids = []
    for v in vectors:
        if v.rid not in unique_vector_rids:
            unique_vector_rids.append(v.rid)

    knowledge_text = ""
    knowledge = []
    for i, rid in enumerate(unique_vector_rids):
        # filters all vectors with same rid
        related_vectors = [v for v in vectors if v.rid == rid]
        knowledge_text += f"Knowledge Object [{i+1}] {rid}\n"

        # if single vector isn't a chunk just append text
        if len(related_vectors) == 1 and not related_vectors[0].is_chunk:
            knowledge_text += f"{related_vectors[0].get_text()}\n\n"
            knowledge.append({
                "knowledge_object_id": i+1,
                "num_vectors": 1,
                "vectors": [related_vectors[0].to_dict()]
            })
        # otherwise append each chunk with a chunk id prefix
        else:
            related_vectors.sort(key=lambda v: v.chunk_id)
            chunks = {
                "knowledge_object_id": i+1,
                "num_vectors": len(related_vectors),
                "vectors": []
            }
            for vector in related_vectors:
                # knowledge_text += f"Chunk {vector.chunk_id}:\n{vector.get_text()}\n\n"
                knowledge_text += f"{vector.get_text()}\n\n"
                chunks["vectors"].append(vector.to_dict())
            knowledge.append(chunks)


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation + [{
            "role": "user",
            "content": query + "\n\n" + knowledge_text
        }]
    )

    # not including knowledge text in conversation history, only active query
    conversation.append({
        "role": "user",
        "content": query,
        "knowledge_text": knowledge_text,
        "knowledge": knowledge
    })

    bot_message = response.choices[0].message.content

    footnote_table = ""
    for n, rid in enumerate(unique_vector_rids):
        line = f"{n+1}: <{rid}>"
        # cited = f"[{n+1}]" in bot_message
        # if not cited: line += " (unused)"
        footnote_table += line + "\n"

        # conversation[-1]["knowledge"][n]["cited"] = cited
    
    conversation.append({
        "role": "assistant",
        "content": bot_message,
        "footnotes": footnote_table
    })

    with open("conversations.json", "w") as f:
        json.dump(conversations, f, indent=2)

    return bot_message + "\n\n" + footnote_table