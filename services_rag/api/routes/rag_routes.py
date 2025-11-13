# api/rag/
from fastapi import APIRouter
from api.dependency import QdrantRepoDep, LLMDep
from utils.vectorize import embed_text
router = APIRouter()

@router.get("/")
async def ask_question(q: str, qdrant_repo: QdrantRepoDep, llm_client: LLMDep):
    query_vector = embed_text(q, True)
    relevant_docs = await qdrant_repo.search_points(query_vector, limit=5)
    print("\n".join(f'{x.payload["text"]} {x.score}' for x in relevant_docs))
    relevant_text = '\n'.join([ x.payload["text"] for x in relevant_docs])
    response_text = llm_client.generate(q, relevant_text)
    return {"message": response_text}

