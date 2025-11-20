# Explanation Image Upload Feature

## Overview
The backend now supports uploading optional explanation images for questions. This feature allows admins to add visual aids when text explanations alone cannot properly convey the concept.

## API Endpoints

### 1. Upload Explanation Image
**POST** `/api/v1/questions/{question_id}/upload-explanation-image`

Upload an explanation image for a specific question.

**Authentication:** Required (Admin only)

**Parameters:**
- `question_id` (path parameter): The ID of the question

**Request Body (multipart/form-data):**
- `file`: Image file (jpg, jpeg, png, gif, webp)
  - Maximum size: 5MB
  - Only image formats allowed

**Response (200 OK):**
```json
{
  "id": 1,
  "exam_type_id": 1,
  "subject_id": 2,
  "question_text": "What is the Pythagorean theorem?",
  "question_type": "multiple_choice",
  "options": {"A": "a² + b² = c²", "B": "a + b = c", "C": "a × b = c", "D": "a - b = c"},
  "correct_answer": "A",
  "explanation": "The Pythagorean theorem states that in a right triangle...",
  "explanation_image": "uploads/explanation_images/123e4567-e89b-12d3-a456-426614174000.png",
  "created_at": "2025-11-09T10:30:00"
}
```

**Error Responses:**
- `404 Not Found`: Question not found
- `400 Bad Request`: Invalid file type or file too large
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user

**Example (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch(`/api/v1/questions/${questionId}/upload-explanation-image`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

const data = await response.json();
console.log('Image uploaded:', data.explanation_image);
```

**Example (Axios):**
```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await axios.post(
  `/api/v1/questions/${questionId}/upload-explanation-image`,
  formData,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'multipart/form-data'
    }
  }
);

console.log('Image uploaded:', response.data.explanation_image);
```

### 2. Delete Explanation Image
**DELETE** `/api/v1/questions/{question_id}/explanation-image`

Remove the explanation image from a question.

**Authentication:** Required (Admin only)

**Parameters:**
- `question_id` (path parameter): The ID of the question

**Response (200 OK):**
```json
{
  "message": "Explanation image deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: Question not found or no image exists
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not an admin user

### 3. Access Uploaded Images
**GET** `/uploads/explanation_images/{filename}`

Retrieve an uploaded explanation image.

**Authentication:** Not required (public access)

**Example:**
```html
<img src="/uploads/explanation_images/123e4567-e89b-12d3-a456-426614174000.png" alt="Explanation diagram" />
```

## Frontend Integration Guide

### Creating Questions with Images

1. **Create the question first** using the existing POST `/api/v1/questions/` endpoint
2. **Upload the explanation image** using the new upload endpoint with the returned question ID
3. The question response will include the `explanation_image` field with the full path

### Updating Questions with Images

1. **Update the image** by calling the upload endpoint (replaces existing image automatically)
2. **Remove the image** by calling the delete endpoint

### Displaying Questions

When displaying a question with an explanation:
```javascript
function renderQuestionExplanation(question) {
  let html = `<div class="explanation">${question.explanation}</div>`;
  
  // Add image if available
  if (question.explanation_image) {
    html += `
      <div class="explanation-image">
        <img 
          src="/${question.explanation_image}" 
          alt="Visual explanation"
          style="max-width: 100%; height: auto;"
        />
      </div>
    `;
  }
  
  return html;
}
```

### File Upload Validation (Frontend)

```javascript
function validateImageFile(file) {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 5 * 1024 * 1024; // 5MB
  
  if (!allowedTypes.includes(file.type)) {
    alert('Please upload a valid image file (JPG, PNG, GIF, or WebP)');
    return false;
  }
  
  if (file.size > maxSize) {
    alert('File size must be less than 5MB');
    return false;
  }
  
  return true;
}
```

## Database Schema Changes

The `questions` table now includes:
- `explanation_image` (VARCHAR, nullable): Stores the file path to the explanation image

## File Storage

- **Directory:** `uploads/explanation_images/`
- **Naming:** Files are stored with UUID-based filenames to avoid conflicts
- **Format:** Original file extension is preserved
- **Cleanup:** Images are automatically deleted when:
  - A question is deleted
  - A new image is uploaded to replace an existing one
  - The delete endpoint is called

## Notes for Frontend Developers

1. **Optional Field:** The `explanation_image` field is optional. Check if it exists before displaying.
2. **Image URLs:** Use the full path returned in the API response (e.g., `uploads/explanation_images/...`)
3. **Admin Only:** Only admin users can upload/delete images. Regular users can only view them.
4. **File Validation:** Validate files on the frontend before upload to improve UX.
5. **Error Handling:** Handle upload errors gracefully (network issues, file size, etc.)

## Testing

Test the feature using these steps:

1. **Create a question** with text explanation only
2. **Upload an image** for that question
3. **Verify the image** appears in the question response
4. **View the image** by accessing the URL directly
5. **Replace the image** by uploading a new one
6. **Delete the image** using the delete endpoint
7. **Verify cleanup** by checking that old images are removed
