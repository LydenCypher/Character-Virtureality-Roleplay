from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Character Interaction API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/ai_character_app')
client = MongoClient(MONGO_URL)
db = client.get_default_database()

# Collections
users_collection = db.users
characters_collection = db.characters
conversations_collection = db.conversations
messages_collection = db.messages

# Security
security = HTTPBearer()

# Pydantic models
class User(BaseModel):
    user_id: str
    username: str
    email: str
    preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class Character(BaseModel):
    character_id: str
    name: str
    description: str
    personality: str
    avatar: Optional[str] = None
    ai_provider: str = "openai"
    system_prompt: str
    is_nsfw: bool = False
    created_by: str
    created_at: datetime
    updated_at: datetime

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    character_id: str
    title: str
    mode: str = "casual"  # casual, rp, rpg
    is_nsfw: bool = False
    created_at: datetime
    updated_at: datetime

class Message(BaseModel):
    message_id: str
    conversation_id: str
    sender: str  # user or character
    content: str
    timestamp: datetime
    ai_provider: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    ai_provider: Optional[str] = "openai"

class CreateCharacterRequest(BaseModel):
    name: str
    description: str
    personality: str
    avatar: Optional[str] = None
    ai_provider: str = "openai"
    system_prompt: str
    is_nsfw: bool = False

class CreateConversationRequest(BaseModel):
    character_id: str
    title: str
    mode: str = "casual"
    is_nsfw: bool = False

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "AI Character Interaction API is running"}

# User management
@app.post("/api/users")
async def create_user(username: str, email: str):
    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        username=username,
        email=email,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_collection.insert_one(user.dict())
    return {"user_id": user_id, "message": "User created successfully"}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Character management
@app.post("/api/characters")
async def create_character(character_data: CreateCharacterRequest, user_id: str):
    character_id = str(uuid.uuid4())
    character = Character(
        character_id=character_id,
        name=character_data.name,
        description=character_data.description,
        personality=character_data.personality,
        avatar=character_data.avatar,
        ai_provider=character_data.ai_provider,
        system_prompt=character_data.system_prompt,
        is_nsfw=character_data.is_nsfw,
        created_by=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    characters_collection.insert_one(character.dict())
    return {"character_id": character_id, "message": "Character created successfully"}

@app.get("/api/characters")
async def get_characters(skip: int = 0, limit: int = 20):
    characters = list(characters_collection.find({}, {"_id": 0}).skip(skip).limit(limit))
    return {"characters": characters}

@app.get("/api/characters/{character_id}")
async def get_character(character_id: str):
    character = characters_collection.find_one({"character_id": character_id}, {"_id": 0})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

# Conversation management
@app.post("/api/conversations")
async def create_conversation(conversation_data: CreateConversationRequest, user_id: str):
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        character_id=conversation_data.character_id,
        title=conversation_data.title,
        mode=conversation_data.mode,
        is_nsfw=conversation_data.is_nsfw,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    conversations_collection.insert_one(conversation.dict())
    return {"conversation_id": conversation_id, "message": "Conversation created successfully"}

@app.get("/api/conversations/{user_id}")
async def get_user_conversations(user_id: str):
    conversations = list(conversations_collection.find({"user_id": user_id}, {"_id": 0}))
    return {"conversations": conversations}

@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    messages = list(messages_collection.find({"conversation_id": conversation_id}, {"_id": 0}).sort("timestamp", 1))
    return {"messages": messages}

# Chat endpoint (placeholder for AI integration)
@app.post("/api/chat")
async def chat(chat_request: ChatRequest):
    # This will be enhanced with actual AI integration
    message_id = str(uuid.uuid4())
    
    # Save user message
    user_message = Message(
        message_id=message_id,
        conversation_id=chat_request.conversation_id,
        sender="user",
        content=chat_request.message,
        timestamp=datetime.utcnow()
    )
    messages_collection.insert_one(user_message.dict())
    
    # Generate AI response (placeholder)
    ai_response = f"This is a placeholder response to: {chat_request.message}"
    
    # Save AI response
    ai_message_id = str(uuid.uuid4())
    ai_message = Message(
        message_id=ai_message_id,
        conversation_id=chat_request.conversation_id,
        sender="character",
        content=ai_response,
        timestamp=datetime.utcnow(),
        ai_provider=chat_request.ai_provider
    )
    messages_collection.insert_one(ai_message.dict())
    
    return {
        "user_message": user_message.dict(),
        "ai_response": ai_message.dict()
    }

# AI providers endpoint
@app.get("/api/ai-providers")
async def get_ai_providers():
    return {
        "providers": [
            {"id": "openai", "name": "OpenAI GPT", "available": True},
            {"id": "anthropic", "name": "Anthropic Claude", "available": True},
            {"id": "gemini", "name": "Google Gemini", "available": False}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)