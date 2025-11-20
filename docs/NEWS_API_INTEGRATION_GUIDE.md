# News API Integration Guide

This guide explains how to integrate the News Feed API into your frontend application.

## Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Authentication](#authentication)
4. [Request/Response Examples](#requestresponse-examples)
5. [Frontend Integration Examples](#frontend-integration-examples)
6. [Error Handling](#error-handling)

---

## Overview

The News API allows you to display curated news items in your application. News items include:
- **title**: The news heading
- **content**: A short description of the news
- **url**: Link to the full article on the internet
- **date**: Publication date of the news
- **created_at**: When the news item was added to the system
- **updated_at**: When the news item was last updated

**Base URL**: `https://vmi2848672.contaboserver.net/cbt/api/v1/news`

---

## API Endpoints

### 1. List All News Items (Public)
**GET** `/api/v1/news`

Retrieve all news items, ordered by publication date (newest first).

**Query Parameters:**
- `skip` (optional, default: 0): Number of items to skip for pagination
- `limit` (optional, default: 100, max: 100): Maximum number of items to return

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "New JAMB Registration Opens",
    "content": "JAMB has announced the opening of registration for the 2025 UTME examination...",
    "url": "https://example.com/jamb-registration-2025",
    "date": "2025-11-10T00:00:00",
    "created_at": "2025-11-10T10:30:00",
    "updated_at": "2025-11-10T10:30:00"
  }
]
```

---

### 2. Get Single News Item (Public)
**GET** `/api/v1/news/{news_id}`

Retrieve a specific news item by ID.

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "New JAMB Registration Opens",
  "content": "JAMB has announced the opening of registration for the 2025 UTME examination...",
  "url": "https://example.com/jamb-registration-2025",
  "date": "2025-11-10T00:00:00",
  "created_at": "2025-11-10T10:30:00",
  "updated_at": "2025-11-10T10:30:00"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "News item with ID 999 not found"
}
```

---

### 3. Create News Item (Admin Only)
**POST** `/api/v1/news`

Create a new news item. **Requires admin authentication.**

**Request Headers:**
```
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "WAEC Releases 2025 Results",
  "content": "The West African Examinations Council has released results for students who sat for the May/June 2025 examinations...",
  "url": "https://example.com/waec-results-2025",
  "date": "2025-11-10T00:00:00"
}
```

**Field Requirements:**
- `title`: Required, 1-500 characters
- `content`: Required, minimum 1 character
- `url`: Required, must be a valid HTTP/HTTPS URL
- `date`: Required, ISO 8601 datetime format

**Response:** `201 Created`
```json
{
  "id": 2,
  "title": "WAEC Releases 2025 Results",
  "content": "The West African Examinations Council has released results...",
  "url": "https://example.com/waec-results-2025",
  "date": "2025-11-10T00:00:00",
  "created_at": "2025-11-10T11:00:00",
  "updated_at": "2025-11-10T11:00:00"
}
```

---

### 4. Update News Item (Admin Only)
**PUT** `/api/v1/news/{news_id}`

Update an existing news item. **Requires admin authentication.**

**Request Headers:**
```
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json
```

**Request Body:** (All fields optional)
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "url": "https://example.com/updated-url",
  "date": "2025-11-11T00:00:00"
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "title": "Updated Title",
  "content": "Updated content...",
  "url": "https://example.com/updated-url",
  "date": "2025-11-11T00:00:00",
  "created_at": "2025-11-10T11:00:00",
  "updated_at": "2025-11-10T12:00:00"
}
```

---

### 5. Delete News Item (Admin Only)
**DELETE** `/api/v1/news/{news_id}`

Delete a news item. **Requires admin authentication.**

**Request Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Response:** `204 No Content`

---

## Authentication

### Public Endpoints (No Authentication Required)
- `GET /api/v1/news` - List all news
- `GET /api/v1/news/{news_id}` - Get single news item

### Admin-Only Endpoints (Authentication Required)
- `POST /api/v1/news` - Create news
- `PUT /api/v1/news/{news_id}` - Update news
- `DELETE /api/v1/news/{news_id}` - Delete news

**How to Authenticate:**
1. Login as admin via `/api/v1/users/login`
2. Include the JWT token in the `Authorization` header:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

---

## Frontend Integration Examples

### Example 1: Fetch and Display News Feed

```javascript
const BACKEND_URL = 'https://vmi2848672.contaboserver.net';
const NEWS_API = `${BACKEND_URL}/cbt/api/v1/news`;

async function loadNewsFeed() {
  try {
    const response = await fetch(NEWS_API);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const newsItems = await response.json();
    displayNews(newsItems);
  } catch (error) {
    console.error('Error loading news:', error);
    showError('Failed to load news feed. Please try again later.');
  }
}

function displayNews(newsItems) {
  const newsContainer = document.getElementById('news-feed');
  newsContainer.innerHTML = ''; // Clear existing content
  
  if (newsItems.length === 0) {
    newsContainer.innerHTML = '<p>No news items available.</p>';
    return;
  }
  
  newsItems.forEach(news => {
    const newsCard = createNewsCard(news);
    newsContainer.appendChild(newsCard);
  });
}

function createNewsCard(news) {
  const card = document.createElement('div');
  card.className = 'news-card';
  
  const date = new Date(news.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  card.innerHTML = `
    <div class="news-header">
      <h3>${escapeHtml(news.title)}</h3>
      <span class="news-date">${date}</span>
    </div>
    <p class="news-content">${escapeHtml(news.content)}</p>
    <a href="${escapeHtml(news.url)}" target="_blank" rel="noopener noreferrer" class="read-more">
      Read Full Article →
    </a>
  `;
  
  return card;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Load news when page loads
document.addEventListener('DOMContentLoaded', loadNewsFeed);
```

---

### Example 2: Create News Item (Admin Panel)

```javascript
const BACKEND_URL = 'https://vmi2848672.contaboserver.net';
const NEWS_API = `${BACKEND_URL}/cbt/api/v1/news`;

async function createNewsItem(newsData) {
  // Get admin token from localStorage
  const token = localStorage.getItem('adminToken');
  
  if (!token) {
    alert('You must be logged in as admin to create news items.');
    return;
  }
  
  try {
    const response = await fetch(NEWS_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(newsData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create news item');
    }
    
    const newNews = await response.json();
    console.log('News created successfully:', newNews);
    
    // Refresh news feed
    await loadNewsFeed();
    
    // Clear form
    document.getElementById('news-form').reset();
    
    alert('News item created successfully!');
  } catch (error) {
    console.error('Error creating news:', error);
    alert(`Error: ${error.message}`);
  }
}

// HTML Form Handler
document.getElementById('create-news-btn').addEventListener('click', async (e) => {
  e.preventDefault();
  
  const newsData = {
    title: document.getElementById('news-title').value,
    content: document.getElementById('news-content').value,
    url: document.getElementById('news-url').value,
    date: new Date(document.getElementById('news-date').value).toISOString()
  };
  
  // Validate required fields
  if (!newsData.title || !newsData.content || !newsData.url || !newsData.date) {
    alert('All fields are required');
    return;
  }
  
  await createNewsItem(newsData);
});
```

---

### Example 3: Pagination for News Feed

```javascript
const BACKEND_URL = 'https://vmi2848672.contaboserver.net';
const NEWS_API = `${BACKEND_URL}/cbt/api/v1/news`;
const ITEMS_PER_PAGE = 10;
let currentPage = 1;

async function loadNewsPage(page = 1) {
  const skip = (page - 1) * ITEMS_PER_PAGE;
  
  try {
    const response = await fetch(`${NEWS_API}?skip=${skip}&limit=${ITEMS_PER_PAGE}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const newsItems = await response.json();
    displayNews(newsItems);
    updatePagination(newsItems.length);
  } catch (error) {
    console.error('Error loading news page:', error);
    showError('Failed to load news. Please try again.');
  }
}

function updatePagination(itemsCount) {
  const hasMore = itemsCount === ITEMS_PER_PAGE;
  
  document.getElementById('prev-btn').disabled = currentPage === 1;
  document.getElementById('next-btn').disabled = !hasMore;
  document.getElementById('page-number').textContent = `Page ${currentPage}`;
}

document.getElementById('prev-btn').addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    loadNewsPage(currentPage);
  }
});

document.getElementById('next-btn').addEventListener('click', () => {
  currentPage++;
  loadNewsPage(currentPage);
});

// Initial load
loadNewsPage(1);
```

---

### Example 4: Update News Item (Admin)

```javascript
async function updateNewsItem(newsId, updatedData) {
  const token = localStorage.getItem('adminToken');
  
  if (!token) {
    alert('You must be logged in as admin to update news items.');
    return;
  }
  
  try {
    const response = await fetch(`${NEWS_API}/${newsId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(updatedData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update news item');
    }
    
    const updated = await response.json();
    console.log('News updated successfully:', updated);
    
    // Refresh news feed
    await loadNewsFeed();
    
    alert('News item updated successfully!');
  } catch (error) {
    console.error('Error updating news:', error);
    alert(`Error: ${error.message}`);
  }
}
```

---

### Example 5: Delete News Item (Admin)

```javascript
async function deleteNewsItem(newsId) {
  const token = localStorage.getItem('adminToken');
  
  if (!token) {
    alert('You must be logged in as admin to delete news items.');
    return;
  }
  
  if (!confirm('Are you sure you want to delete this news item?')) {
    return;
  }
  
  try {
    const response = await fetch(`${NEWS_API}/${newsId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete news item');
    }
    
    console.log('News deleted successfully');
    
    // Refresh news feed
    await loadNewsFeed();
    
    alert('News item deleted successfully!');
  } catch (error) {
    console.error('Error deleting news:', error);
    alert(`Error: ${error.message}`);
  }
}
```

---

## Error Handling

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "Failed to create news item: <error details>"
}
```

**401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**
```json
{
  "detail": "Only admins can perform this action"
}
```

**404 Not Found**
```json
{
  "detail": "News item with ID 123 not found"
}
```

**422 Unprocessable Entity** (Validation Error)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### Error Handling Best Practices

```javascript
async function handleApiCall(apiFunction) {
  try {
    return await apiFunction();
  } catch (error) {
    // Network errors
    if (error.message.includes('fetch')) {
      showError('Network error. Please check your connection.');
      return;
    }
    
    // API errors
    if (error.response) {
      const status = error.response.status;
      
      switch (status) {
        case 401:
          showError('Please log in to continue.');
          redirectToLogin();
          break;
        case 403:
          showError('You do not have permission to perform this action.');
          break;
        case 404:
          showError('The requested item was not found.');
          break;
        case 422:
          showError('Invalid data. Please check your input.');
          break;
        default:
          showError('An error occurred. Please try again.');
      }
    }
    
    console.error('Error:', error);
  }
}
```

---

## CSS Styling Example

```css
/* News Feed Styles */
.news-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.news-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.news-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2em;
  flex: 1;
}

.news-date {
  color: #666;
  font-size: 0.9em;
  white-space: nowrap;
  margin-left: 15px;
}

.news-content {
  color: #555;
  line-height: 1.6;
  margin-bottom: 15px;
}

.read-more {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
  display: inline-block;
  transition: color 0.3s ease;
}

.read-more:hover {
  color: #0056b3;
  text-decoration: underline;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #007bff;
  background: white;
  color: #007bff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination button:hover:not(:disabled) {
  background: #007bff;
  color: white;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## Complete HTML Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>News Feed</title>
  <link rel="stylesheet" href="news-styles.css">
</head>
<body>
  <div class="container">
    <header>
      <h1>Latest News</h1>
    </header>
    
    <main>
      <div id="news-feed"></div>
      
      <div class="pagination">
        <button id="prev-btn">← Previous</button>
        <span id="page-number">Page 1</span>
        <button id="next-btn">Next →</button>
      </div>
    </main>
  </div>
  
  <script src="news-api.js"></script>
</body>
</html>
```

---

## Testing the API

You can test the API endpoints using curl:

```bash
# List all news items
curl https://vmi2848672.contaboserver.net/cbt/api/v1/news

# Get specific news item
curl https://vmi2848672.contaboserver.net/cbt/api/v1/news/1

# Create news item (requires admin token)
curl -X POST https://vmi2848672.contaboserver.net/cbt/api/v1/news \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test News",
    "content": "This is a test news item",
    "url": "https://example.com/test",
    "date": "2025-11-10T00:00:00"
  }'
```

---

## Support

For questions or issues with the News API, please contact the backend development team or refer to the API documentation at:
`https://vmi2848672.contaboserver.net/cbt/api/v1/docs`
