# CBT (Computer Based Test) Application - Backend

A comprehensive Computer Based Test application built with FastAPI using Domain-Driven Design (DDD) architecture.

## Features

- **User Management**: Registration, authentication, and user profiles
- **Test Management**: Create, update, and manage tests
- **Question Bank**: Manage questions with multiple types (multiple choice, true/false, essay)
- **Test Taking**: Start attempts, submit answers, and track progress
- **Results & Analytics**: View detailed results and performance analytics
- **Categories**: Organize tests and questions by categories

## Architecture

The application follows DDD principles with clear separation of concerns:

- **Domain**: Core business logic and entities
- **Application**: Use cases, commands, and handlers
- **Infrastructure**: Database, external services
- **Presentation**: API routes and controllers

## API Endpoints

### Users
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Categories
- `POST /api/v1/categories/` - Create category
- `GET /api/v1/categories/` - List categories
- `GET /api/v1/categories/{category_id}` - Get category
- `PUT /api/v1/categories/{category_id}` - Update category
- `DELETE /api/v1/categories/{category_id}` - Delete category

### Tests
- `POST /api/v1/tests/` - Create test
- `GET /api/v1/tests/` - List tests
- `GET /api/v1/tests/{test_id}` - Get test
- `GET /api/v1/tests/{test_id}/with-questions` - Get test with questions
- `GET /api/v1/tests/category/{category_id}` - Get tests by category
- `PUT /api/v1/tests/{test_id}` - Update test
- `DELETE /api/v1/tests/{test_id}` - Delete test

### Questions
- `POST /api/v1/questions/` - Create question
- `POST /api/v1/questions/bulk` - Create multiple questions
- `GET /api/v1/questions/test/{test_id}` - Get questions by test
- `GET /api/v1/questions/category/{category_id}` - Get questions by category
- `GET /api/v1/questions/{question_id}` - Get question
- `PUT /api/v1/questions/{question_id}` - Update question
- `DELETE /api/v1/questions/{question_id}` - Delete question

### Attempts
- `POST /api/v1/attempts/start` - Start test attempt
- `POST /api/v1/attempts/submit` - Submit test attempt
- `GET /api/v1/attempts/user/{user_id}` - Get user attempts
- `GET /api/v1/attempts/{attempt_id}` - Get attempt details

### Results
- `GET /api/v1/results/attempt/{attempt_id}` - Get attempt result
- `GET /api/v1/results/user/{user_id}` - Get user results
- `GET /api/v1/results/test/{test_id}/analytics` - Get test analytics

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Set up PostgreSQL database:
```sql
CREATE DATABASE cbt_db;
```

4. Run database migrations:
```bash
source venv/bin/activate
alembic upgrade head
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Database Schema

The application uses the following main entities:
- **Users**: User accounts and authentication
- **Categories**: Test and question categorization
- **Tests**: Test definitions and settings
- **Questions**: Question bank with various types
- **Attempts**: Test taking sessions
- **Answers**: User responses to questions

## Question Types Supported

- **Multiple Choice**: Questions with predefined options
- **True/False**: Boolean questions
- **Essay**: Open-ended text responses

## Database Migrations

This project uses **Alembic** for database migrations. See [docs/ALEMBIC_GUIDE.md](docs/ALEMBIC_GUIDE.md) for detailed instructions.

**Quick commands:**
```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Check current migration status
alembic current
```

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization

## Documentation

- [Alembic Migration Guide](docs/ALEMBIC_GUIDE.md) - Database migration instructions
- [Explanation Image Upload](docs/EXPLANATION_IMAGE_UPLOAD.md) - Image upload feature documentation
- [Testing Guide](docs/TESTING_GUIDE.md) - Testing procedures