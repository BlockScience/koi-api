from langchain_text_splitters import RecursiveCharacterTextSplitter
from rid_lib.core import RID

from koi.config import (
    PINECONE_BATCH_SIZE,
    VOYAGEAI_BATCH_SIZE,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from .base import pinecone_index, voyage_embed_texts
from .vector_object import VectorObject


class VectorInterface:
    embedding_queue = []
    queue_limit = 100

    def __init__(self, rid: RID):
        self.rid = rid

    def embed(self, flush_queue=False):
        cached_object = self.rid.cache.read()

        if cached_object.json_data is None or "text" not in cached_object.json_data:
            print("cache empty or missing text field, can't embed")
            return False
        
        text = cached_object.json_data["text"]
        meta = cached_object.metadata
        del meta["files"]
        meta["text"] = text

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        chunks = []
        for doc in text_splitter.create_documents([text]):
            chunk_text = doc.page_content
            start = text.find(chunk_text)
            end = start + len(chunk_text)
            chunks.append({
                "text": chunk_text,
                "start": start,
                "end": end
            })

        if len(chunks) == 1:
            self.embedding_queue.append([
                str(self.rid), text, meta
            ])
            print(f"added {self.rid} to embedding queue")

        else:
            for i, chunk in enumerate(chunks):
                rid_fragment = self.create_rid_fragment_string(self.rid, i)
                chunk_text = chunk["text"]
                chunk_meta = {
                    **meta,
                    "character_length": len(chunk_text),
                    "text": chunk_text,
                    "chunk_start": chunk["start"],
                    "chunk_end": chunk["end"],
                    "chunk_id": i,
                    "num_chunks": len(chunks)
                }

                print(f"{self.rid} chunk {i+1}/{len(chunks)} [{chunk['start']}:{chunk['end']}]")
                
                self.embedding_queue.append([
                    rid_fragment, chunk_text, chunk_meta
                ])
            print(f"added {self.rid} to embedding queue ({len(chunks)} chunks)")

        if flush_queue is True or len(self.embedding_queue) > self.queue_limit:
            self.embed_queue()

    @classmethod
    def embed_queue(cls):
        print(f"flushing {len(cls.embedding_queue)} objects from embedding queue")

        ids, texts, metas = list(zip(*cls.embedding_queue))

        embeddings = []
        while len(embeddings) < len(cls.embedding_queue):
            start = len(embeddings)
            end = min(start + VOYAGEAI_BATCH_SIZE, len(cls.embedding_queue))
            embeddings.extend(voyage_embed_texts(texts[start:end]))
            print(f"created embeddings for {end} objects")

        print(f"resulting in {len(embeddings)} embeddings")
        
        vectors = list(zip(
            ids, embeddings, metas
        ))

        pinecone_index.upsert(
            vectors=vectors, batch_size=PINECONE_BATCH_SIZE
        )
        cls.embedding_queue = []

    def get_vector_ids(self, return_vectors=False):
        """
        If the RID is not chunked, it will have one vector where the id is its RID. If the RID is chunked, its id will take the form '{RID}#chunk:{id}'. It will test both possible starting ids to determine whether the RID is chunked, and find the other ids if it is.
        """

        rid_fragment_str = self.create_rid_fragment_string(self.rid, 0)
        potential_ids = [
            str(self.rid),
            rid_fragment_str
        ]

        result = pinecone_index.fetch(potential_ids)
        vectors = result["vectors"]

        vector_ids = []

        if str(self.rid) in vectors:
            vector_ids.append(str(self.rid))
        elif rid_fragment_str in vectors:
            num_chunks = int(vectors[rid_fragment_str]["metadata"]["num_chunks"])
            for chunk_id in range(num_chunks):
                vector_ids.append(
                    self.create_rid_fragment_string(self.rid, chunk_id)
                )
        
        if return_vectors:
            return vector_ids, vectors
        else:
            return vector_ids

    def read(self):
        vector_ids, vectors = self.get_vector_ids(return_vectors=True)

        if len(vector_ids) == 1:
            vector_id = vector_ids[0]
            return [
                VectorObject(vectors[vector_id])
            ]
        
        elif len(vector_ids) > 1:
            result = pinecone_index.fetch(vector_ids)
            chunk_vectors = result["vectors"]

            return [
                VectorObject(chunk_vectors[vector_id])
                for vector_id in vector_ids
            ]

        else:
            return []
        
    def delete(self):
        vector_ids = self.get_vector_ids()
        if vector_ids:
            return pinecone_index.delete(self.get_vector_ids())
        else:
            return {}

    @staticmethod
    def create_rid_fragment_string(rid, chunk_id):
        return f"{rid}#chunk:{chunk_id}"
    
    @staticmethod
    def query(text, top_k=10, filter={"character_length": {"$gt": 200}}):
        result = pinecone_index.query(
            vector=voyage_embed_texts([text], input_type="query"),
            filter=filter,
            top_k=top_k,
            include_metadata=True
        )
        vectors = result["matches"]

        return [
            VectorObject(v) for v in vectors
        ]
    
    @staticmethod
    def drop():
        pinecone_index.delete(delete_all=True)
