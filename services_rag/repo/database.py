from typing import List, Tuple, Optional, Union
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct, ScoredPoint, PointIdsList, PointsSelector, Filter,Distance, VectorParams
from qdrant_client.http import models

from fastapi import HTTPException
import uuid
# TODO: Use Env vars
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "rag_chunks"
VECTOR_SIZE = 768

class QdrantRepository:
    """
    Data Access Layer (Repository) for Qdrant operations.
    
    This class is instantiated via Dependency Injection in main.py, 
    receiving the single, application-scoped AsyncQdrantClient instance.
    """
    
    def __init__(self, client: AsyncQdrantClient):
        self.client = client
        self.collection_name = COLLECTION_NAME
        self.vector_size = VECTOR_SIZE

    async def insert_point(self, text_vector_tuple: Tuple[str, List[float]]) -> dict:
        """Inserts or updates a single vector point along with its payload."""
        text, vector = text_vector_tuple
        
        if len(vector) != self.vector_size:
            raise HTTPException(status_code=400, detail=f"Vector size must be {self.vector_size}.")
            
        vector_id = str(uuid.uuid4())
        payload = {"text": text}
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=vector_id,
                    vector=vector, 
                    payload=payload
                )
            ],
            wait=True # Wait for the operation to complete
        )
        return {"status": "success", "message": f"Point {vector_id} inserted/updated."}

    async def bulk_insert_points(self, text_vector_tuples: List[Tuple[str, List[float]]]) -> dict:
        """Inserts or updates multiple vector points along with their payloads."""
        points = []
        for text, vector in text_vector_tuples:
            if len(vector) != self.vector_size:
                raise HTTPException(status_code=400, detail=f"Vector size must be {self.vector_size}.")
                
            vector_id = str(uuid.uuid4())
            payload = {"text": text.replace(".. ", ". ")}
            points.append(
                PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload=payload
                )
            )
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True # Wait for the operation to complete
        )
        return {"status": "success", "message": f"{len(points)} points inserted/updated."}

    async def search_points(self, query_vector: List[float], limit: int = 1) -> List[ScoredPoint]:
        """Performs a vector similarity search."""
        if len(query_vector) != self.vector_size:
            raise HTTPException(status_code=400, detail=f"Query vector size must be {self.vector_size}.")
            
        print(query_vector)
        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True # Retrieve the original data (payload)
        )
        return search_result

    async def delete_point(self, vector_id: str) -> dict:
        """Deletes a single point by ID."""
        
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=[vector_id]),
            wait=True
        )
        return {"status": "success", "message": f"Point {vector_id} deleted."}
    
    async def clear_collection(self) -> dict:
        """Clears all points from the collection by deleting and recreating it."""
        
        try:
            collections = await self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                await self.client.delete_collection(collection_name=self.collection_name)
                print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")
        
        # Recreate the collection
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            on_disk_payload=True,
        hnsw_config=models.HnswConfigDiff(
            on_disk=True,  # Store index on disk, not just memory
            m=16,
            ef_construct=100
        ),
        optimizers_config=models.OptimizersConfigDiff(
            deleted_threshold=0.2,
            vacuum_min_vector_number=1000,
            default_segment_number=2,  # Fewer segments = less complexity
            max_segment_size=50000,
            memmap_threshold=20000,    # Use memory mapping carefully
            indexing_threshold=10000,
            flush_interval_sec=10,     # More frequent flushing
            max_optimization_threads=2
        ),
        wal_config=models.WalConfigDiff(
            wal_capacity_mb=16,        # Smaller WAL = less corruption risk
            wal_segments_ahead=0       # No segments ahead
        )
        )
        print(f"Recreated collection: {self.collection_name}")
        
        return {"status": "success", "message": "Collection cleared and recreated."}