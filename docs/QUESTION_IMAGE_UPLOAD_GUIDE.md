# Question Image Upload - Frontend Integration Guide

## Overview
The backend now supports uploading **question images** in addition to explanation images. This allows admins to upload questions as images when text alone cannot adequately represent the question (e.g., diagrams, charts, mathematical equations, graphs, etc.).

## Key Differences: Question Image vs Explanation Image

| Feature | Question Image | Explanation Image |
|---------|---------------|-------------------|
| **Purpose** | Display the question itself | Display the explanation after answering |
| **When Shown** | When presenting the question to students | After student submits answer |
| **Use Case** | Questions with diagrams, charts, graphs | Visual explanations of correct answers |
| **Field Name** | `question_image` | `explanation_image` |
| **Upload Endpoint** | `/upload-question-image` | `/upload-explanation-image` |
| **Storage Path** | `/cbt/uploads/question_images/` | `/cbt/uploads/explanation_images/` |

## API Endpoints

### 1. Upload Question Image
**POST** `/api/v1/questions/{question_id}/upload-question-image`

Upload an image representing the question itself.

**Authentication:** Required (Admin only)

**Request:**
```javascript
// Headers
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

// Body
{
  file: <image_file>  // jpg, jpeg, png, gif, webp (max 5MB)
}
```

**Response (200 OK):**
```json
{
  "id": 123,
  "exam_type_id": 1,
  "subject_id": 2,
  "question_text": "Refer to the diagram above",
  "question_image": "/cbt/uploads/question_images/a1b2c3d4-e5f6-7890-abcd-ef1234567890.png",
  "question_type": "multiple_choice",
  "options": {
    "A": "Option 1",
    "B": "Option 2",
    "C": "Option 3",
    "D": "Option 4"
  },
  "correct_answer": "A",
  "explanation": "The correct answer is...",
  "explanation_image": null,
  "created_at": "2025-11-09T10:30:00"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid file type or file too large
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not an admin
- `404 Not Found` - Question not found

### 2. Delete Question Image
**DELETE** `/api/v1/questions/{question_id}/question-image`

Remove the question image from a question.

**Authentication:** Required (Admin only)

**Response (200 OK):**
```json
{
  "message": "Question image deleted successfully"
}
```

### 3. Access Question Image
**GET** `/uploads/question_images/{filename}`

Retrieve the uploaded question image.

**Authentication:** Not required (public access)

**Full URL Format:**
```
https://vmi2848672.contaboserver.net/cbt/uploads/question_images/{filename}
```

## Frontend Implementation Examples

### Admin Panel - Creating Questions with Images

```javascript
// Admin creates a question with an image
async function createQuestionWithImage(questionData, imageFile) {
  const API_BASE = 'https://vmi2848672.contaboserver.net/cbt/api/v1';
  const token = localStorage.getItem('adminToken');
  
  // Step 1: Create the question first
  const questionResponse = await fetch(`${API_BASE}/questions/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      exam_type_id: questionData.examTypeId,
      subject_id: questionData.subjectId,
      question_text: questionData.text,
      question_type: 'multiple_choice',
      options: questionData.options,
      correct_answer: questionData.correctAnswer,
      explanation: questionData.explanation
    })
  });
  
  const question = await questionResponse.json();
  
  // Step 2: Upload question image if provided
  if (imageFile) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    const imageResponse = await fetch(
      `${API_BASE}/questions/${question.id}/upload-question-image`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      }
    );
    
    const updatedQuestion = await imageResponse.json();
    return updatedQuestion;
  }
  
  return question;
}

// Usage
const imageFile = document.getElementById('questionImageInput').files[0];
const question = await createQuestionWithImage({
  examTypeId: 1,
  subjectId: 2,
  text: 'Refer to the diagram above. What is the area of the shaded region?',
  options: {
    A: '25 cm²',
    B: '30 cm²',
    C: '35 cm²',
    D: '40 cm²'
  },
  correctAnswer: 'B',
  explanation: 'Area = length × width = 5 × 6 = 30 cm²'
}, imageFile);
```

### Admin Panel - File Upload Validation

```javascript
function validateQuestionImage(file) {
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

// HTML
<input 
  type="file" 
  id="questionImageInput" 
  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
  onChange={(e) => {
    const file = e.target.files[0];
    if (file && validateQuestionImage(file)) {
      // Preview the image
      const reader = new FileReader();
      reader.onload = (event) => {
        document.getElementById('imagePreview').src = event.target.result;
      };
      reader.readAsDataURL(file);
    }
  }}
/>
<img id="imagePreview" style="max-width: 300px; display: none;" />
```

### Student View - Displaying Questions with Images

```javascript
function renderQuestion(question) {
  const BASE_URL = 'https://vmi2848672.contaboserver.net';
  
  let html = '<div class="question-container">';
  
  // Display question image if available
  if (question.question_image) {
    html += `
      <div class="question-image-wrapper">
        <img 
          src="${BASE_URL}${question.question_image}" 
          alt="Question diagram"
          class="question-image"
          onerror="this.style.display='none'"
        />
      </div>
    `;
  }
  
  // Display question text
  html += `
    <div class="question-text">
      <h3>Question ${question.id}</h3>
      <p>${question.question_text}</p>
    </div>
  `;
  
  // Display options
  html += '<div class="question-options">';
  for (const [key, value] of Object.entries(question.options)) {
    html += `
      <label class="option">
        <input type="radio" name="answer" value="${key}" />
        <span>${key}. ${value}</span>
      </label>
    `;
  }
  html += '</div>';
  html += '</div>';
  
  return html;
}

// CSS for question images
const styles = `
.question-image-wrapper {
  margin: 20px 0;
  text-align: center;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
}

.question-image {
  max-width: 100%;
  height: auto;
  max-height: 400px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .question-image {
    max-height: 300px;
  }
}
`;
```

### Results Page - Displaying Questions with Explanations

```javascript
function renderQuestionWithAnswer(question, userAnswer, isCorrect) {
  const BASE_URL = 'https://vmi2848672.contaboserver.net';
  
  let html = '<div class="result-question">';
  
  // Question section
  html += '<div class="question-section">';
  
  // Question image (if available)
  if (question.question_image) {
    html += `
      <div class="question-image-wrapper">
        <img 
          src="${BASE_URL}${question.question_image}" 
          alt="Question"
          class="question-image"
        />
      </div>
    `;
  }
  
  html += `
    <p class="question-text">${question.question_text}</p>
  `;
  
  // Show user's answer and correct answer
  html += `
    <div class="answer-comparison">
      <p class="${isCorrect ? 'correct' : 'incorrect'}">
        Your answer: ${userAnswer} 
        ${isCorrect ? '✓' : '✗'}
      </p>
      ${!isCorrect ? `<p class="correct-answer">Correct answer: ${question.correct_answer}</p>` : ''}
    </div>
  `;
  
  html += '</div>'; // End question-section
  
  // Explanation section
  html += '<div class="explanation-section">';
  html += '<h4>Explanation:</h4>';
  html += `<p>${question.explanation}</p>`;
  
  // Explanation image (if available)
  if (question.explanation_image) {
    html += `
      <div class="explanation-image-wrapper">
        <img 
          src="${BASE_URL}${question.explanation_image}" 
          alt="Explanation"
          class="explanation-image"
        />
      </div>
    `;
  }
  
  html += '</div>'; // End explanation-section
  html += '</div>'; // End result-question
  
  return html;
}
```

### React/Vue Component Example

```jsx
// React Component
import React, { useState } from 'react';

const QuestionDisplay = ({ question }) => {
  const BASE_URL = 'https://vmi2848672.contaboserver.net';
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  
  return (
    <div className="question-container">
      {/* Question Image */}
      {question.question_image && (
        <div className="question-image-wrapper">
          <img 
            src={`${BASE_URL}${question.question_image}`}
            alt="Question diagram"
            className="question-image"
            onError={(e) => e.target.style.display = 'none'}
          />
        </div>
      )}
      
      {/* Question Text */}
      <div className="question-text">
        <h3>Question {question.id}</h3>
        <p>{question.question_text}</p>
      </div>
      
      {/* Options */}
      <div className="question-options">
        {Object.entries(question.options).map(([key, value]) => (
          <label key={key} className="option">
            <input
              type="radio"
              name="answer"
              value={key}
              checked={selectedAnswer === key}
              onChange={() => setSelectedAnswer(key)}
            />
            <span>{key}. {value}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default QuestionDisplay;
```

## Best Practices

### 1. Image Optimization
Before uploading, optimize images:
- Compress images to reduce file size
- Use appropriate formats (PNG for diagrams, JPG for photos)
- Recommended max dimensions: 1200x1200px

### 2. Fallback Handling
Always provide meaningful `question_text` even when using images:
```javascript
// Good ✓
question_text: "Refer to the diagram above. What is the area of triangle ABC?"

// Bad ✗
question_text: "See image"
```

### 3. Accessibility
Add proper alt text and ensure images load correctly:
```html
<img 
  src="${questionImage}" 
  alt="Geometric diagram showing triangle ABC with sides labeled"
  onerror="handleImageError()"
/>
```

### 4. Loading States
Show loading indicators while images load:
```javascript
const [imageLoading, setImageLoading] = useState(true);

<img 
  src={questionImage}
  onLoad={() => setImageLoading(false)}
  style={{ display: imageLoading ? 'none' : 'block' }}
/>
{imageLoading && <div className="image-loader">Loading image...</div>}
```

## Testing Checklist

- [ ] Upload question image successfully
- [ ] Image appears in question list
- [ ] Image displays correctly in test view
- [ ] Image shows in results/review
- [ ] Replace existing image works
- [ ] Delete image works
- [ ] Image error handling works (broken links)
- [ ] Mobile responsive display
- [ ] Works alongside explanation images
- [ ] File validation prevents invalid uploads

## Common Use Cases

### When to Use Question Images
1. **Mathematical equations** - Complex formulas or expressions
2. **Diagrams** - Geometric shapes, circuit diagrams, etc.
3. **Charts & Graphs** - Data visualization questions
4. **Maps** - Geography questions
5. **Scientific illustrations** - Biology diagrams, chemistry structures
6. **Tables** - Complex data tables

### When to Use Explanation Images
1. **Step-by-step solutions** - Visual breakdown of the solution
2. **Annotated diagrams** - Highlighting correct parts
3. **Comparative images** - Before/after, correct/incorrect
4. **Detailed illustrations** - Clarifying the explanation

## Troubleshooting

### Image Not Displaying
1. Check if `question_image` field is not null
2. Verify full URL is correct: `${BASE_URL}${question.question_image}`
3. Check browser console for 404 errors
4. Ensure CORS is properly configured

### Upload Fails
1. Verify file size < 5MB
2. Check file type is allowed (jpg, png, gif, webp)
3. Ensure admin authentication token is valid
4. Check network connection

### Image Quality Issues
1. Upload higher resolution images
2. Use PNG for diagrams (better quality)
3. Use JPG for photographs (smaller size)
4. Avoid uploading screenshots (use original images)

## API Response Structure

```typescript
interface Question {
  id: number;
  exam_type_id: number;
  subject_id: number;
  question_text: string;
  question_image: string | null;  // NEW: URL path to question image
  question_type: 'multiple_choice' | 'true_false' | 'essay';
  options: Record<string, string> | null;
  correct_answer: string;
  explanation: string | null;
  explanation_image: string | null;  // URL path to explanation image
  created_at: string;
}
```

## Support

For questions or issues:
1. Check this documentation
2. Review the backend API at `/cbt/api/v1/docs`
3. Check the EXPLANATION_IMAGE_UPLOAD.md for similar patterns

---

**Summary:** Question images allow you to present questions as visual content, while explanation images help clarify answers. Both work independently and can be used together for comprehensive question presentation.
