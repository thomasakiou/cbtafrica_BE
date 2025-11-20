# Explanation Image Upload Feature - Implementation Summary

## Overview
Successfully implemented optional explanation image upload functionality for questions in the CBT Africa backend.

## Changes Made

### 1. Database Model (`app/infrastructure/database/models.py`)
- Added `explanation_image` field to the `Question` model
- Type: `String` (nullable)
- Stores the file path to uploaded explanation images

### 2. Schemas (`app/domain/questions/schemas.py`)
- Updated `QuestionBase` schema to include `explanation_image` field
- Updated `QuestionUpdate` schema to allow updating `explanation_image`
- All schemas now support the optional image field

### 3. Configuration (`app/config.py`)
- Added file upload configuration:
  - `UPLOAD_DIR`: Directory for storing images (`uploads/explanation_images`)
  - `MAX_FILE_SIZE`: Maximum file size (5MB)
  - `ALLOWED_IMAGE_EXTENSIONS`: Supported formats (jpg, jpeg, png, gif, webp)

### 4. Routes (`app/presentation/routes/questions.py`)
**New Imports:**
- Added `UploadFile`, `File`, `Form` from FastAPI
- Added `os`, `uuid`, `Path` for file handling

**New Function:**
- `save_explanation_image()`: Helper function to validate and save uploaded images
  - Validates file extension
  - Validates file size
  - Creates unique filename using UUID
  - Saves file to disk
  - Returns file path

**New Endpoints:**
- `POST /api/v1/questions/{question_id}/upload-explanation-image`
  - Upload explanation image for a question
  - Admin only
  - Replaces existing image if present
  - Returns updated question with image path

- `DELETE /api/v1/questions/{question_id}/explanation-image`
  - Delete explanation image for a question
  - Admin only
  - Removes file from disk and database

**Updated Endpoints:**
- `DELETE /api/v1/questions/{question_id}`
  - Now also deletes associated explanation image file when deleting a question

### 5. Main Application (`main.py`)
- Added import for `StaticFiles` and `Path`
- Created upload directory on startup
- Mounted static files at `/uploads` route to serve uploaded images
- Images are publicly accessible at `/uploads/explanation_images/{filename}`

### 6. Database Migration (`migrations/add_explanation_image_column.sql`)
- Created SQL migration script for manual database updates
- Adds `explanation_image` column to questions table
- Note: Auto-applied via SQLAlchemy's `create_all()` on app restart

### 7. Documentation (`docs/EXPLANATION_IMAGE_UPLOAD.md`)
- Complete API documentation for frontend developers
- Endpoint details with request/response examples
- Integration guide with code examples
- File validation guidelines
- Testing procedures

## File Structure
```
cbtafrica_BE/
├── app/
│   ├── config.py                          # Updated: Added upload settings
│   ├── domain/
│   │   └── questions/
│   │       └── schemas.py                 # Updated: Added explanation_image field
│   ├── infrastructure/
│   │   └── database/
│   │       └── models.py                  # Updated: Added explanation_image column
│   └── presentation/
│       └── routes/
│           └── questions.py               # Updated: Added upload endpoints
├── docs/
│   └── EXPLANATION_IMAGE_UPLOAD.md        # New: Feature documentation
├── migrations/
│   └── add_explanation_image_column.sql   # New: Database migration
├── uploads/
│   └── explanation_images/                # New: Upload directory
└── main.py                                # Updated: Static files mounting
```

## API Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/questions/{id}/upload-explanation-image` | Upload explanation image | Admin |
| DELETE | `/api/v1/questions/{id}/explanation-image` | Delete explanation image | Admin |
| GET | `/uploads/explanation_images/{filename}` | Access uploaded image | Public |

## Frontend Integration Steps

1. **Create Question**: Use existing POST `/api/v1/questions/` endpoint
2. **Upload Image**: POST to `/api/v1/questions/{id}/upload-explanation-image` with multipart form data
3. **Display Image**: Use the returned `explanation_image` path in an `<img>` tag
4. **Update Image**: POST again to replace (old image auto-deleted)
5. **Delete Image**: DELETE to `/api/v1/questions/{id}/explanation-image`

## Features

✅ Optional explanation images for questions  
✅ File validation (type and size)  
✅ Secure file storage with UUID filenames  
✅ Automatic cleanup on deletion/replacement  
✅ Public image access via static files  
✅ Admin-only upload permissions  
✅ Multiple image format support  
✅ 5MB file size limit  

## Next Steps for Deployment

1. **Apply Database Migration** (if not using auto-create):
   ```bash
   psql -d cbt_db -f migrations/add_explanation_image_column.sql
   ```

2. **Restart Application**:
   ```bash
   # The upload directory will be created automatically
   # Database schema will be updated via SQLAlchemy
   python main.py
   ```

3. **Test Endpoints**:
   - Use Swagger UI at `/api/v1/docs` to test the upload endpoint
   - Upload a test image and verify it's accessible

4. **Frontend Integration**:
   - Share `docs/EXPLANATION_IMAGE_UPLOAD.md` with frontend team
   - Implement file upload UI in the question creation/edit forms

## Security Considerations

- ✅ File type validation (only images allowed)
- ✅ File size limit (5MB max)
- ✅ Admin-only upload access
- ✅ UUID-based filenames prevent path traversal
- ✅ Automatic cleanup prevents orphaned files
- ⚠️ Consider adding rate limiting for upload endpoint
- ⚠️ Consider adding image optimization/compression

## Notes

- Images are optional - questions work without them
- Existing questions remain unchanged (NULL explanation_image)
- The field is backward compatible with the frontend
- Images persist across server restarts
- Upload directory is created automatically on startup
