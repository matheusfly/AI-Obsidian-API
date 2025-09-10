#!/usr/bin/env python3
"""
FastAPI Template
A basic FastAPI application template
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Your API",
    description="API Description",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

# In-memory storage (replace with database in production)
items_db = []

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to your API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/items", response_model=List[ItemResponse])
async def get_items():
    """Get all items"""
    return items_db

@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    """Create a new item"""
    item_id = len(items_db) + 1
    new_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description
    }
    items_db.append(new_item)
    return new_item

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get item by ID"""
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
