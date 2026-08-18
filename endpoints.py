from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Form
from pydantic import BaseModel, Field

from backend.app.services.rag_engine import rag_engine
from backend.app.core.logging_config import logger

router = APIRouter()


# Request / Response Schemas
class QueryRequest(BaseModel):
    query: str = Field(..., description="Search query or question for enterprise knowledge base.")
    top_k: Optional[int] = Field(default=4, ge=1, le=20, description="Top K vector chunks to retrieve.")
    confidence_threshold: Optional[float] = Field(default=0.35, ge=0.0, le=1.0, description="Minimum confidence score threshold.")
    session_id: Optional[str] = Field(default="default_session", description="Session identifier for chat history.")
    filter_doc_id: Optional[str] = Field(default=None, description="Optional document ID to restrict search scope.")
    llm_provider: Optional[str] = Field(default=None, description="LLM provider: 'fallback', 'openai', or 'ollama'.")
    openai_api_key: Optional[str] = Field(default=None, description="Optional OpenAI API key for generation.")


class QueryResponse(BaseModel):
    query: str
    answer: str
    provider: str
    confidence_score: float
    citations: List[dict]
    total_retrieved: int


class DocumentDeleteResponse(BaseModel):
    doc_id: str
    removed_chunks: int
    status: str


# Endpoints
@router.get("/health", tags=["System Diagnostics"])
def health_check():
    """
    System Health Diagnostic Endpoint.
    Returns status of service, vector database, and models.
    """
    try:
        health_info = rag_engine.get_system_health()
        return health_info
    except Exception as e:
        logger.error(f"Health check diagnostic error: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/api/v1/upload", tags=["Document Management"])
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None)
):
    """
    Uploads and indexes an enterprise document (PDF, DOCX, TXT).
    Processes text, splits into semantic chunks, generates vector embeddings, and stores in ChromaDB.
    """
    allowed_extensions = ["pdf", "docx", "txt"]
    ext = file.filename.split(".")[-1].lower() if file.filename else ""
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '.{ext}'. Supported extensions are: {', '.join(allowed_extensions)}"
        )

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        res = rag_engine.process_and_index_document(
            filename=file.filename,
            content=content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return res
    except ValueError as ve:
        logger.warning(f"Validation error during document upload '{file.filename}': {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing document upload '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process and index document: {str(e)}")


@router.post("/api/v1/query", response_model=QueryResponse, tags=["RAG Search & Q&A"])
def rag_query(request: QueryRequest):
    """
    Executes RAG similarity search and generates context-grounded answers with exact source citations.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        result = rag_engine.query(
            query_text=request.query,
            top_k=request.top_k,
            confidence_threshold=request.confidence_threshold,
            session_id=request.session_id,
            filter_doc_id=request.filter_doc_id,
            llm_provider=request.llm_provider,
            openai_api_key=request.openai_api_key
        )
        return result
    except Exception as e:
        logger.error(f"Error during RAG query execution: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query execution failed: {str(e)}")


@router.get("/api/v1/documents", tags=["Document Management"])
def list_documents():
    """
    Lists all indexed enterprise documents and their metadata summary.
    """
    try:
        docs = rag_engine.list_indexed_documents()
        return {"total_documents": len(docs), "documents": docs}
    except Exception as e:
        logger.error(f"Failed to list indexed documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/v1/documents/{doc_id}", response_model=DocumentDeleteResponse, tags=["Document Management"])
def delete_document(doc_id: str):
    """
    Deletes an indexed document and its associated vector embeddings from ChromaDB.
    """
    try:
        res = rag_engine.delete_indexed_document(doc_id)
        if res["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Document with doc_id '{doc_id}' not found.")
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document '{doc_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/chat-history", tags=["Chat & Audit History"])
def get_chat_history(session_id: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=200)):
    """
    Retrieves past Q&A session history and citation audit logs.
    """
    try:
        history = rag_engine.history_manager.get_history(session_id=session_id, limit=limit)
        return {"total_records": len(history), "history": history}
    except Exception as e:
        logger.error(f"Failed to fetch chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/v1/chat-history", tags=["Chat & Audit History"])
def clear_chat_history(session_id: Optional[str] = Query(None)):
    """
    Clears Q&A interaction logs from history database.
    """
    try:
        deleted_count = rag_engine.history_manager.clear_history(session_id=session_id)
        return {"status": "success", "records_cleared": deleted_count}
    except Exception as e:
        logger.error(f"Failed to clear chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
