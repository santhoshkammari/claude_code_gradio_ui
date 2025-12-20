from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import anthropic
from typing import Optional
import asyncio
from pathlib import Path
from src.mcp_tools.web import async_web_search
from database import ChatDatabase


app = FastAPI(title="Claude API", version="1.0.0")
db = ChatDatabase()

# Mount static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5


class ClaudeRequest(BaseModel):
    message: str
    option1: str  # "claudecode" or "qwen"
    option2: str  # model name like "Claude Sonnet 4.5"


@app.get("/")
async def read_root():
    """
    Serve the main HTML page
    """
    html_path = Path(__file__).parent / "index.html"
    return FileResponse(html_path)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "healthy", "message": "Claude API is running"}


@app.post("/rbi")
async def claude_message(request: MessageRequest):
    pass


from src.agents.agent_search import search_agent


@app.post("/claude")
async def search_agent(request: ClaudeRequest):
    async def generate_stream():
        response = await search_agent(request.message)
        words = response.split(' ')
        for word in words:
            yield f"data: {word} \n\n"
            await asyncio.sleep(0.05) 

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/sample")
async def sample(request: ClaudeRequest):
    """
    Claude streaming endpoint that mimics LLM token-by-token response
    Later this will be replaced with actual LLM integration
    """
    async def generate_stream():
        # Dummy response that will be streamed token by token
        dummy_response = f"""Hello! I received your message: "{request.message}"

You selected:
- Mode: {request.option1}
- Model: {request.option2}

This is a dummy streaming response to demonstrate the streaming functionality.
In the future, this will be replaced with actual LLM responses from Claude or Qwen.

The system is working correctly and ready for integration with real language models.
Each word is being streamed token by token to simulate real LLM behavior.
This provides a smooth user experience with progressive text rendering.

Thank you for testing the Claudable interface!"""

        # Split into words and stream with delay
        words = dummy_response.split(' ')
        for word in words:
            yield f"data: {word} \n\n"
            await asyncio.sleep(0.05)  # Simulate processing delay

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


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


# New Chat Session Endpoints

@app.post("/api/chat/create")
async def create_chat(request: ClaudeRequest):
    """
    Create a new chat session with the first message
    Returns the chat UUID
    """
    try:
        # Generate title from first message
        title = db.generate_title_from_message(request.message)

        # Create chat session
        chat_uuid = db.create_chat(title=title)

        # Add user message
        db.add_message(chat_uuid, "user", request.message)

        return JSONResponse({
            "chat_uuid": chat_uuid,
            "title": title
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/{chat_uuid}")
async def serve_chat_page(chat_uuid: str):
    """
    Serve the chat page for a specific chat session
    """
    # Verify chat exists
    chat = db.get_chat(chat_uuid)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    html_path = Path(__file__).parent / "chat.html"
    return FileResponse(html_path)


@app.get("/api/chats")
async def get_all_chats():
    """
    Get all chat sessions
    """
    try:
        chats = db.get_all_chats()
        return JSONResponse({"chats": chats})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/{chat_uuid}/messages")
async def get_chat_messages(chat_uuid: str):
    """
    Get all messages for a specific chat
    """
    try:
        chat = db.get_chat(chat_uuid)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        messages = db.get_messages(chat_uuid)
        return JSONResponse({
            "chat": chat,
            "messages": messages
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/{chat_uuid}/message")
async def send_message_to_chat(chat_uuid: str, request: ClaudeRequest):
    """
    Send a message to an existing chat and stream the response
    """
    # Verify chat exists
    chat = db.get_chat(chat_uuid)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Add user message to database
    db.add_message(chat_uuid, "user", request.message)
    print("@@")
    print(request.message)

    async def generate_stream():
        response = await search_agent(request.message)

        # Store the complete response
        complete_response = ""

        words = response.split(' ')
        for word in words:
            complete_response += word + " "
            yield f"data: {word} \n\n"
            await asyncio.sleep(0.05)

        # Save assistant's response to database
        db.add_message(chat_uuid, "assistant", complete_response.strip())

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.delete("/api/chat/{chat_uuid}")
async def delete_chat(chat_uuid: str):
    """
    Delete a chat session
    """
    try:
        chat = db.get_chat(chat_uuid)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        db.delete_chat(chat_uuid)
        return JSONResponse({"message": "Chat deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
