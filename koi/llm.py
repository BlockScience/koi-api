import json

from openai import OpenAI, RateLimitError, APIConnectionError
import nanoid

from .llm_subsystem import rag, prompts

from .config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)

try:
    with open("conversations.json", "r") as f:
        conversations = json.load(f)
except FileNotFoundError:
    conversations = {}




def start_conversation(conversation_id=None):
    """Creates a new conversation with provided id, or generates one randomly."""
    conversation_id = conversation_id or nanoid.generate()
    conversations[conversation_id] = [prompts.SYSTEM_PROMPT]
    return conversation_id

def continue_conversation(conversation_id, prompt: str):
    """Continues conversation, returns response."""
    conversation = conversations.get(conversation_id)
    if conversation is None:
        start_conversation(conversation_id)
    conversation = conversations.get(conversation_id)

    # remove bot mention
    prompt = prompt.split(maxsplit=1)[1]
    
    if (prompt.startswith(("+", "-"))):
        print('detected filter')
        params, query = prompt.split(maxsplit=1)
                        
        if params.startswith("+"):
            op = "in"
        elif params.startswith("-"):
            op = "nin"
            
        spaces = params[1:].split(";")
        
        print(params, spaces)
        
        filter = {
            "character_length": {"$gt": 200},
            "space": {"$" + op: spaces},
        }
    else:
        query = prompt
        filter = {
            "character_length": {"$gt": 200}
        }
        
    print(filter)

    
    queries = rag.generate_queries([
        *conversation,
        {
            "role": "user",
            "content": query
        }
    ])

    print(f"DERIVED QUERIES: {queries}")
    vectors = rag.vector_multiquery(queries, top_k=5, filter=filter)
    unique_vector_rids = rag.unique_vector_rids(vectors)
    knowledge_text = rag.generate_knowledge(unique_vector_rids, vectors)
            
    
    messages = conversation + [{
        "role": "user",
        "content": query + "\n\n" + knowledge_text
    }]
        
    print("SENDING REQUEST TO OPENAI:")
    print(f"ORIGINAL QUERY: {query}")
    print(f"KNOWLEDGE: total {len(knowledge_text)} characters")
    print(f"TOTAL CONVERSATION: {len(json.dumps(messages))}")
    
    with open("prompt_to_chatbot.json", "w") as f:
        json.dump(messages, f, indent=2)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
    except RateLimitError:
        return "Exceeded OpenAI maximum token limit, please start a new thread"
    
    except APIConnectionError:
        return "Error connecting to OpenAI API"

    # not including knowledge text in conversation history, only active query
    conversation.append({
        "role": "user",
        "content": query
    })

    bot_message = response.choices[0].message.content

    footer = "---\nGenerated from sources: "
    for n, rid in enumerate(unique_vector_rids):
        if getattr(rid, "url", None):
            footer += f"<{rid.url}|{n+1}>"
        else:
            footer += f"<rid:{rid}|{n+1}>"
        
        if n < len(unique_vector_rids) - 1:
            footer += ", "
            
    footer += f"\nwith filter `{filter}`"
    
    # footer += "\nusing{:.1f}k prompt tokens".format(response.usage.prompt_tokens / 1000.0)
            
                
    conversation.append({
        "role": "assistant",
        "content": bot_message,
        # "footnotes": footnotes
    })

    with open("conversations.json", "w") as f:
        json.dump(conversations, f, indent=2)

    return bot_message + "\n\n" + footer