# Add to main.py
from fastapi.responses import FileResponse
import os

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    else:
        # Return a minimal 1x1 pixel favicon
        return Response(
            content=b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00\x68\x04\x00\x00\x16\x00\x00\x00',
            media_type="image/x-icon"
        )
