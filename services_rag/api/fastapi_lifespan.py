from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, HTTPException
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http import models

from llm.base import BaseLLM
from llm.gemini import GeminiLLM
from llm.local import LocalLLM
import time

# TODO: use env vars
QDRANT_URL      = "http://localhost:6333"
COLLECTION_NAME = "rag_chunks"
VECTOR_SIZE     = 768
DISTANCE        = Distance.COSINE
GEMINI_KEY      = "AIzaSyCUEK1CzuJRdEnKncFpazd3vwtMzS8rHH8"   # <- env var in real life


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
   """
   Create singletons once, close them on shutdown.
   """
   try:
      qc = AsyncQdrantClient(url=QDRANT_URL)
      if not await qc.collection_exists(COLLECTION_NAME):
         await qc.create_collection(
               collection_name=COLLECTION_NAME,
               vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
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

   except ResponseHandlingException as e:
      # 3. Handle the specific Qdrant connection error
      # This will catch the 'All connection attempts failed' error
      print("="*60)
      print("CRITICAL ERROR: Could not connect to Qdrant service.")
      print("   Connection error details:", e)
      print("="*60)
      

   llm: BaseLLM = GeminiLLM(GEMINI_KEY)
   # llm: BaseLLM = LocalLLM("not-needed")


   app.state.qdrant = qc
   app.state.llm = llm

   yield          # <-- server is now running

   # 4.  Cleanup
   await qc.close()
   if hasattr(llm, "close"):
      await llm.close()
