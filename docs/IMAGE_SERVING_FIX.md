# Image Serving Fix

## Problem
Images were not accessible through the public URL because:
1. FastAPI's `root_path="/cbt"` was set for reverse proxy
2. Static files mount (`app.mount()`) doesn't work properly with `root_path`
3. Nginx strips `/cbt` prefix before proxying to FastAPI

## Solution
Replaced `StaticFiles` mount with a custom route handler:

```python
@app.get("/uploads/explanation_images/{filename}")
async def serve_explanation_image(filename: str):
    """Serve explanation images"""
    file_path = Path("uploads/explanation_images") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)
```

## How It Works
1. Nginx receives: `https://vmi2848672.contaboserver.net/cbt/uploads/explanation_images/file.png`
2. Nginx proxies to: `http://localhost:8002/uploads/explanation_images/file.png`
3. FastAPI route handler serves the file from disk

## Testing
```bash
# Test locally
curl -I http://localhost:8002/uploads/explanation_images/ce88069c-eb04-4d7b-b3b3-2c0a3a6a46ef.png

# Test publicly
curl -I https://vmi2848672.contaboserver.net/cbt/uploads/explanation_images/ce88069c-eb04-4d7b-b3b3-2c0a3a6a46ef.png
```

Both should return `200 OK` with `content-type: image/png`.

## Database Path Format
Images are stored in the database with the full URL path:
```
/cbt/uploads/explanation_images/uuid-filename.png
```

This ensures the frontend can construct the correct URL:
```
https://vmi2848672.contaboserver.net/cbt/uploads/explanation_images/uuid-filename.png
```
