# Quick Start Guide: Testing Explanation Image Upload

## Prerequisites
- Backend server running
- Admin account credentials
- Test image file (JPG, PNG, GIF, or WebP)

## Step 1: Start the Server
```bash
cd /root/cbtafrica_BE
python main.py
```

The server should create the `uploads/explanation_images/` directory automatically.

## Step 2: Get Admin Token

Login as admin to get an access token:

```bash
curl -X POST "http://localhost:8002/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_admin_password"
  }'
```

Save the `access_token` from the response.

## Step 3: Create or Get a Question

Create a test question (or use an existing one):

```bash
curl -X POST "http://localhost:8002/api/v1/questions/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_type_id": 1,
    "subject_id": 1,
    "question_text": "What is the Pythagorean theorem?",
    "question_type": "multiple_choice",
    "options": {
      "A": "a² + b² = c²",
      "B": "a + b = c",
      "C": "a × b = c",
      "D": "a - b = c"
    },
    "correct_answer": "A",
    "explanation": "The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides."
  }'
```

Note the `id` in the response.

## Step 4: Upload Explanation Image

Upload an image for the question:

```bash
curl -X POST "http://localhost:8002/api/v1/questions/1/upload-explanation-image" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/image.png"
```

Replace:
- `1` with your question ID
- `/path/to/your/image.png` with actual image path
- `YOUR_ACCESS_TOKEN` with your token

## Step 5: Verify Upload

The response should include the `explanation_image` field:

```json
{
  "id": 1,
  "exam_type_id": 1,
  "subject_id": 1,
  "question_text": "What is the Pythagorean theorem?",
  ...
  "explanation_image": "uploads/explanation_images/550e8400-e29b-41d4-a716-446655440000.png",
  ...
}
```

## Step 6: Access the Image

Open in browser or curl:

```bash
# View in browser
http://localhost:8002/uploads/explanation_images/550e8400-e29b-41d4-a716-446655440000.png

# Or download with curl
curl -O "http://localhost:8002/uploads/explanation_images/550e8400-e29b-41d4-a716-446655440000.png"
```

## Step 7: Test Image Replacement

Upload a different image to replace the existing one:

```bash
curl -X POST "http://localhost:8002/api/v1/questions/1/upload-explanation-image" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/another/image.jpg"
```

The old image should be automatically deleted.

## Step 8: Test Image Deletion

Delete the explanation image:

```bash
curl -X DELETE "http://localhost:8002/api/v1/questions/1/explanation-image" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "message": "Explanation image deleted successfully"
}
```

## Using Swagger UI (Easier Testing)

1. Open browser: `http://localhost:8002/api/v1/docs`
2. Click "Authorize" button and enter your token
3. Navigate to Questions section
4. Find `POST /api/v1/questions/{question_id}/upload-explanation-image`
5. Click "Try it out"
6. Enter question ID
7. Upload file
8. Execute

## Test Validation

### Valid Files
- `test.jpg` (under 5MB)
- `diagram.png` (under 5MB)
- `chart.gif` (under 5MB)
- `graph.webp` (under 5MB)

### Invalid Files (Should Fail)
- `document.pdf` - Wrong file type
- `large_image.jpg` (over 5MB) - File too large
- `video.mp4` - Wrong file type

## Troubleshooting

### "File not found" error
- Check that the uploads directory exists: `ls -la uploads/explanation_images/`
- If missing, restart the server or create manually: `mkdir -p uploads/explanation_images`

### "Permission denied" error
- Check directory permissions: `chmod 755 uploads/ uploads/explanation_images/`

### "Unauthorized" error
- Verify your token is valid
- Check that you're using an admin account
- Token might be expired (default: 8 days)

### Image not displaying
- Check the full URL matches the path in the database
- Ensure static files are mounted correctly in main.py
- Verify the file exists: `ls uploads/explanation_images/`

## Frontend Testing

Create a simple HTML form for testing:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Image Upload</title>
</head>
<body>
    <h1>Upload Explanation Image</h1>
    
    <form id="uploadForm">
        <label>Question ID:</label>
        <input type="number" id="questionId" required><br><br>
        
        <label>Access Token:</label>
        <input type="text" id="token" required><br><br>
        
        <label>Image File:</label>
        <input type="file" id="imageFile" accept="image/*" required><br><br>
        
        <button type="submit">Upload</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const questionId = document.getElementById('questionId').value;
            const token = document.getElementById('token').value;
            const file = document.getElementById('imageFile').files[0];
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch(
                    `http://localhost:8002/api/v1/questions/${questionId}/upload-explanation-image`,
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        body: formData
                    }
                );
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('result').innerHTML = `
                        <h3>Success!</h3>
                        <p>Image uploaded: ${data.explanation_image}</p>
                        <img src="http://localhost:8002/${data.explanation_image}" 
                             style="max-width: 500px;" />
                    `;
                } else {
                    document.getElementById('result').innerHTML = `
                        <h3>Error</h3>
                        <p>${data.detail}</p>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <h3>Error</h3>
                    <p>${error.message}</p>
                `;
            }
        });
    </script>
</body>
</html>
```

Save as `test_upload.html` and open in browser.
