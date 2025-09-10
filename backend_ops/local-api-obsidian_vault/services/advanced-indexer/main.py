from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Advanced Indexer Service",
    description="Advanced indexing service for complex file processing",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "advanced-indexer"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Advanced Indexer Service is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
