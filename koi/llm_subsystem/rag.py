from koi.vectorstore import VectorInterface
from .core import openai_client
from .prompts import QUERY_GENERATION_PROMPT

def generate_queries(conversation):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            QUERY_GENERATION_PROMPT,
            {
                "role": "user",
                "content": "\n".join([
                    msg["role"] + ": " + msg["content"]
                    for msg in conversation
                ])
            }
        ]
    )
    
    query_text = response.choices[0].message.content
    queries = [
        line for line in query_text.splitlines()
        if line != ""
    ]
    return queries[:3]

def vector_multiquery(queries, top_k, filter):
    vectors = set()
    for query in queries:
        vectors.update(VectorInterface.query(query, top_k, filter))
        
    return vectors

def unique_vector_rids(vectors):
    # removes duplicates in the case of multiple chunks from the same document
    unique_vector_rids = []
    for v in vectors:
        if v.rid not in unique_vector_rids:
            unique_vector_rids.append(v.rid)
            
    return unique_vector_rids

def generate_knowledge(unique_vector_rids, vectors):    
    print("received", len(unique_vector_rids), "unique objects")

    knowledge_text = ""
    knowledge = []
    for i, rid in enumerate(unique_vector_rids):
        # filters all vectors with same rid
        related_vectors = [v for v in vectors if v.rid == rid]
        knowledge_text += f"========================\n\nKnowledge Object {i+1}, CITE AS [{i+1}]:\n\n"
        
        # if single vector isn't a chunk just append text
        if len(related_vectors) == 1 and not related_vectors[0].is_chunk:
            knowledge_text += f"{related_vectors[0].get_extended_text()}\n\n"
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
                knowledge_text += f"{vector.get_extended_text()}\n\n"
                chunks["vectors"].append(vector.to_dict())
            knowledge.append(chunks)
            
    print("combined into", len(knowledge), "knowledge objects")
            
    return knowledge_text