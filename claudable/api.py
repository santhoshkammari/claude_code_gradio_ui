from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import anthropic
from typing import Optional
from src.mcp_tools.web import async_web_search


app = FastAPI(title="Claude API", version="1.0.0")


class MessageRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "healthy", "message": "Claude API is running"}


@app.post("/rbi")
async def claude_message(request: MessageRequest):
    pass


@app.post("/web")
async def web_search_endpoint(request: WebSearchRequest):
    """
    Web search endpoint that performs a search using async_web_search
    """
    try:
        results = await async_web_search(request.query, request.max_results)
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
