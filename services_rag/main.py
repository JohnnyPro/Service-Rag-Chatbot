from fastapi import FastAPI
from api.routes.rag_routes import router as rag_router
from api.routes.data_ingest import router as data_ingest_router
from api.fastapi_lifespan import lifespan

app = FastAPI(
    title="RAG API",
    version="1.0.0",
    description="RAG Based service querying",
    lifespan=lifespan
)

@app.on_event("startup")
async def on_startup():
    print("Server starting...")

@app.on_event("shutdown")
async def on_shutdown():
    print("Server shutting down...")
    
    
@app.get('/')
async def root():
    return {"message": "Server is UP"}

app.include_router(rag_router, prefix="/rag", tags=["RAG"])
app.include_router(data_ingest_router, prefix="/data", tags=["Data Ingestion"])