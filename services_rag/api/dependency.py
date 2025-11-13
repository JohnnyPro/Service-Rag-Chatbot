from typing import Annotated
from fastapi import Request, HTTPException, Depends
from qdrant_client import AsyncQdrantClient

from llm.base import BaseLLM
from repo.database import QdrantRepository


def _get_qdrant(request: Request) -> AsyncQdrantClient:
    if not (client := request.app.state.qdrant):
        raise HTTPException(503, "Qdrant not ready")
    return client


def _get_qdrant_repo(request: Request) -> QdrantRepository:
    return QdrantRepository(_get_qdrant(request))


def _get_llm(request: Request) -> BaseLLM:
    if not (llm := request.app.state.llm):
        raise HTTPException(503, "LLM not ready")
    return llm


QdrantRepoDep = Annotated[QdrantRepository, Depends(_get_qdrant_repo)]
LLMDep        = Annotated[BaseLLM, Depends(_get_llm)]