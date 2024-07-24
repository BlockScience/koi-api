from langchain_text_splitters import RecursiveCharacterTextSplitter
from rid_lib.core import RID, DataObject

from koi.config import (
    PINECONE_BATCH_SIZE,
    VOYAGEAI_BATCH_SIZE,
    EMBEDDING_QUEUE_LIMIT,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from koi import utils
from .connectors import pinecone_index, voyage_embed_texts
from .object_model import VectorObject


class VectorInterface:
    """Interface to the vectorstore representation of an RID object.
    
    A VectorInterface is automatically generated and bound to all RID 
    objects as the 'vector' property (see extensions.py). It provides
    access to functions viewing and modifying an RID's vector embeddings.

    Example:
        import koi
        from rid_lib.core import RID

        rid = RID.from_string("example.rid:string")
        rid.cache.write(from_dereference=True)
        rid.vector.embed(from_cache=True, flush_queue=True)
        print(rid.vector.read())

    An RID can have 0 to n associated vectors. RIDs with large text
    fields are split into chunks when embedded creating multiple vector
    objects for better RAG performance.
    """

    embedding_queue = []

    def __init__(self, rid: RID):
        self.rid = rid

    def embed(
            self,
            data_object: DataObject | None = None,
            from_dereference: bool = False,
            from_cache: bool = False,
            flush_queue=False
        ) -> None:
        """Adds an RID object to the embedding queue.

        Currently reads JSON data from cache, and looks for a text field
        to embed. Text is chunked if exceeding maximum chunk size, and
        added to embedding queue in the following format:

            [rid_str, text, metadata]

        For chunks, "#chunk:{id}" is appended to the end of the rid_str.
        If the queue exceeds the queue_limit, or flush_queue is set to
        true, embed_queue is called, embedding all of the queued chunks.
        """

        if sum([
            data_object is not None,
            from_dereference, 
            from_cache
        ]) != 1:
            raise Exception(
                "Call to embed must pass in DataObject OR set "
                "from_dereference = True OR set from_cache = True"
            )

        if data_object is not None:
            if not data_object.json_data:
                print("DataObject doesn't contain JSON data")
                return False
            elif "text" not in data_object.json_data:
                print("DataObject data missing 'text' field")
                return False
            
        if from_dereference:
            data_object = self.rid.dereference()
            if not data_object.json_data:
                print("Dereference didn't return JSON data")
                return False
            elif "text" not in data_object.json_data:
                print("Dereferenced data missing 'text' field")
                return False
        
        if data_object is not None:
            text = data_object.json_data["text"]
            metadata = utils.generate_metadata(self.rid, data_object)

        if from_cache:
            cache_object = self.rid.cache.read()
            if not cache_object.json_data:
                print("Cache empty or doesn't contain JSON data")
                return False
            elif "text" not in cache_object.json_data:
                print("Cache data missing 'text' field")
                return False
            
            text = cache_object.json_data["text"]
            metadata = cache_object.metadata


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
                str(self.rid), text, metadata
            ])
            print(f"added {self.rid} to embedding queue")

        else:
            for i, chunk in enumerate(chunks):
                rid_fragment = self.create_rid_fragment_string(self.rid, i)
                chunk_text = chunk["text"]
                chunk_meta = {
                    **metadata,
                    "character_length": len(chunk_text),
                    "chunk_start": chunk["start"],
                    "chunk_end": chunk["end"],
                    "chunk_id": i,
                    "num_chunks": len(chunks)
                }

                print(f"{self.rid} chunk {i+1}/{len(chunks)} "
                    f"[{chunk['start']}:{chunk['end']}]")
                
                self.embedding_queue.append([
                    rid_fragment, chunk_text, chunk_meta
                ])
            print(f"added {self.rid} to embedding queue ({len(chunks)} chunks)")

        if flush_queue is True or len(self.embedding_queue) > EMBEDDING_QUEUE_LIMIT:
            self.embed_queue()

        return True

    @classmethod
    def embed_queue(cls) -> None:
        """Embeds all objects in the embedding queue."""
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

    def get_vector_ids(
            self,
            return_vectors=False
        ) -> list[str] | tuple[list[str], dict]:
        """Returns a list of all vector ids associated with RID object.

        If 'return_vectors' is set to True, a list of the raw vector
        dicts returned by the pinecone API will also be returned.

        If an RID object is not chunked, it will have a single vector
        with an id equal to the RID. If the RID object is chunked, it
        will have multiple vectors with ids in the form of 
        '{RID}#chunk:{id}'.
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

    def read(self) -> list[VectorObject]:
        """Returns a list of all VectorObjects associated with RID object."""
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
        
    def delete(self) -> dict:
        """Deletes all vectors associated with RID object."""
        vector_ids = self.get_vector_ids()
        if vector_ids:
            return pinecone_index.delete(self.get_vector_ids())
        else:
            return {}

    @staticmethod
    def create_rid_fragment_string(rid, chunk_id) -> str:
        """Generates RID fragment string.
        
        RID fragments are chunk ids append to RIDs to represent multiple
        vectors resulting from a chunked RID object.
        """
        return f"{rid}#chunk:{chunk_id}"
    
    @staticmethod
    def query(
        text,
        top_k=15,
        filter={
            "character_length": {
                "$gt": 200
            }
        }
    ) -> list[VectorObject]:
        """Returns a list of VectorObjects resulting from provided query."""
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
    def drop() -> None:
        """Deletes all vectors."""
        pinecone_index.delete(delete_all=True)
