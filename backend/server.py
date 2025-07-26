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
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# AI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Available AI models
AVAILABLE_MODELS = {
    "openai": {
        "models": ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o4-mini", "o3-mini", "o3", "o1-mini", "gpt-4o-mini", "gpt-4.5-preview", "gpt-4o", "o1", "o1-pro"],
        "default": "gpt-4.1"
    },
    "anthropic": {
        "models": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
        "default": "claude-sonnet-4-20250514"
    },
    "gemini": {
        "models": ["gemini-2.5-flash-preview-04-17", "gemini-2.5-pro-preview-05-06", "gemini-2.0-flash", "gemini-2.0-flash-preview-image-generation", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
        "default": "gemini-2.0-flash"
    }
}

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
    ai_model: str = "gpt-4.1"
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
    ai_provider: str = "openai"
    ai_model: str = "gpt-4.1"
    created_at: datetime
    updated_at: datetime

class Message(BaseModel):
    message_id: str
    conversation_id: str
    sender: str  # user or character
    content: str
    timestamp: datetime
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    ai_provider: Optional[str] = "openai"
    ai_model: Optional[str] = "gpt-4.1"

class CreateCharacterRequest(BaseModel):
    name: str
    description: str
    personality: str
    avatar: Optional[str] = None
    ai_provider: str = "openai"
    ai_model: str = "gpt-4.1"
    system_prompt: str
    is_nsfw: bool = False

class CreateConversationRequest(BaseModel):
    character_id: str
    title: str
    mode: str = "casual"
    is_nsfw: bool = False
    ai_provider: str = "openai"
    ai_model: str = "gpt-4.1"

# Helper functions
def get_api_key(provider: str) -> str:
    """Get API key for the specified provider"""
    if provider == "openai":
        return OPENAI_API_KEY
    elif provider == "anthropic":
        return ANTHROPIC_API_KEY
    elif provider == "gemini":
        # Add Gemini API key when provided
        return os.environ.get('GEMINI_API_KEY')
    return None

def create_character_system_prompt(character: dict, mode: str = "casual") -> str:
    """Create a system prompt for the character based on mode"""
    base_prompt = f"""You are {character['name']}, a character with the following traits:

Description: {character['description']}
Personality: {character['personality']}

Custom Instructions: {character.get('system_prompt', '')}

"""
    
    if mode == "rp":
        base_prompt += """You are engaging in roleplay. Stay in character, be creative, and respond as if you are this character in a story or scene. Use descriptive language and actions in your responses."""
    elif mode == "rpg":
        base_prompt += """You are in an RPG-style interaction. Think of this as a role-playing game where you can describe actions, environments, and consequences. Be engaging and interactive, allowing the user to make choices that affect the story."""
    elif mode == "casual":
        base_prompt += """You are having a casual conversation. Be friendly, engaging, and stay true to your character's personality while having a natural chat."""
    
    if character.get('is_nsfw', False):
        base_prompt += "\n\nNote: This character supports mature/NSFW content when appropriate to the conversation."
    
    return base_prompt

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
    user = users_collection.find_one({"user_id": user_id}, {"_id": 0})
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
        ai_model=character_data.ai_model,
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
        ai_provider=conversation_data.ai_provider,
        ai_model=conversation_data.ai_model,
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

# AI Chat endpoint
@app.post("/api/chat")
async def chat(chat_request: ChatRequest):
    try:
        # Get conversation details
        conversation = conversations_collection.find_one({"conversation_id": chat_request.conversation_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get character details
        character = characters_collection.find_one({"character_id": conversation["character_id"]})
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Use conversation's AI settings or request settings
        ai_provider = chat_request.ai_provider or conversation.get("ai_provider", "openai")
        ai_model = chat_request.ai_model or conversation.get("ai_model", "gpt-4.1")
        
        # Get API key
        api_key = get_api_key(ai_provider)
        if not api_key:
            raise HTTPException(status_code=400, detail=f"API key not configured for {ai_provider}")
        
        # Save user message
        user_message_id = str(uuid.uuid4())
        user_message = Message(
            message_id=user_message_id,
            conversation_id=chat_request.conversation_id,
            sender="user",
            content=chat_request.message,
            timestamp=datetime.utcnow()
        )
        messages_collection.insert_one(user_message.dict())
        
        # Create system prompt based on character and mode
        system_prompt = create_character_system_prompt(character, conversation.get("mode", "casual"))
        
        # Create AI chat instance
        chat_instance = LlmChat(
            api_key=api_key,
            session_id=chat_request.conversation_id,
            system_message=system_prompt
        ).with_model(ai_provider, ai_model)
        
        # Send message to AI
        user_msg = UserMessage(text=chat_request.message)
        ai_response = await chat_instance.send_message(user_msg)
        
        # Save AI response
        ai_message_id = str(uuid.uuid4())
        ai_message = Message(
            message_id=ai_message_id,
            conversation_id=chat_request.conversation_id,
            sender="character",
            content=ai_response,
            timestamp=datetime.utcnow(),
            ai_provider=ai_provider,
            ai_model=ai_model
        )
        messages_collection.insert_one(ai_message.dict())
        
        return {
            "user_message": user_message.dict(),
            "ai_response": ai_message.dict(),
            "ai_provider": ai_provider,
            "ai_model": ai_model
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# AI providers endpoint
@app.get("/api/ai-providers")
async def get_ai_providers():
    providers = []
    
    for provider, config in AVAILABLE_MODELS.items():
        api_key = get_api_key(provider)
        providers.append({
            "id": provider,
            "name": provider.title(),
            "available": api_key is not None,
            "models": config["models"],
            "default_model": config["default"]
        })
    
    return {"providers": providers}

# Update conversation AI settings
@app.put("/api/conversations/{conversation_id}/ai-settings")
async def update_conversation_ai_settings(conversation_id: str, ai_provider: str, ai_model: str):
    conversation = conversations_collection.find_one({"conversation_id": conversation_id})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Validate provider and model
    if ai_provider not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid AI provider: {ai_provider}")
    
    if ai_model not in AVAILABLE_MODELS[ai_provider]["models"]:
        raise HTTPException(status_code=400, detail=f"Invalid model for {ai_provider}: {ai_model}")
    
    # Update conversation
    conversations_collection.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"ai_provider": ai_provider, "ai_model": ai_model, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "AI settings updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)