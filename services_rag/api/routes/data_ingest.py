# api/data/
from fastapi import APIRouter
from utils.helpers import transform_dict_to_text_chunk, transform_doc_id_to_url
from utils.vectorize import embed_text
from utils.data_loader import load_services_from_google_doc
from api.dependency import QdrantRepoDep

router = APIRouter()

@router.post("ingest-id")
async def ingest_data(docId: str, qdrant_repo: QdrantRepoDep):
    doc_url = transform_doc_id_to_url(docId)
    chunks = load_services_from_google_doc(doc_url)
    success = await embed_and_store(chunks, qdrant_repo)
    if success:
        return {"status": "Data ingested", "num_chunks": len(chunks)}
    
    return {"status": "Data ingestion failed"}



@router.post("ingest-url")
async def ingest_data(url: str, qdrant_repo: QdrantRepoDep):
    chunks = load_services_from_google_doc(url)
    success = await embed_and_store(chunks, qdrant_repo)
    if success:
        return {"status": "Data ingested", "num_chunks": len(chunks)}

    return {"status": "Data ingestion failed"}


async def embed_and_store(chunks: list[dict], qdrant_repo: QdrantRepoDep):
    await qdrant_repo.clear_collection()
    text_and_vectors = []
    for chunk in chunks:
        text = transform_dict_to_text_chunk(chunk)
        embedding = embed_text(text)
        text_and_vectors.append((text, embedding))
    
    await qdrant_repo.bulk_insert_points(text_and_vectors)
    return True