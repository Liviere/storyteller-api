# Story Teller API

REST API for managing stories built with FastAPI.

## Features

- Create, read, update, and delete stories
- Filter stories by genre, author, and publication status
- Publish/unpublish stories
- SQLite database with SQLAlchemy ORM
- Automatic API documentation with Swagger UI
- CORS support for frontend integration

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone or navigate to the project directory:

```bash
cd /home/livierek/projekty/story-teller
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

5. Run the application:

```bash
python main.py
```

The API will be available at:

- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Stories

- `POST /api/v1/stories/` - Create a new story
- `GET /api/v1/stories/` - Get all stories (with filtering options)
- `GET /api/v1/stories/{story_id}` - Get a specific story
- `PUT /api/v1/stories/{story_id}` - Update a story
- `DELETE /api/v1/stories/{story_id}` - Delete a story
- `PATCH /api/v1/stories/{story_id}/publish` - Publish a story
- `PATCH /api/v1/stories/{story_id}/unpublish` - Unpublish a story

### Query Parameters for GET /api/v1/stories/

- `skip` (int): Number of stories to skip (default: 0)
- `limit` (int): Number of stories to return (default: 10, max: 100)
- `genre` (string): Filter by genre
- `author` (string): Filter by author (partial match)
- `published_only` (bool): Show only published stories (default: false)

## Example Usage

### Create a Story

```bash
curl -X POST "http://localhost:8000/api/v1/stories/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "The Adventure Begins",
       "content": "Once upon a time in a distant land...",
       "author": "John Doe",
       "genre": "Fantasy",
       "is_published": false
     }'
```

### Get All Stories

```bash
curl "http://localhost:8000/api/v1/stories/"
```

### Get Stories with Filters

```bash
curl "http://localhost:8000/api/v1/stories/?genre=Fantasy&published_only=true&limit=5"
```

## Development

### Project Structure

```
story-teller/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   └── story.py
├── schemas/               # Pydantic schemas
│   ├── __init__.py
│   └── story.py
├── routers/               # API route handlers
│   ├── __init__.py
│   └── stories.py
└── database/              # Database configuration
    ├── __init__.py
    └── connection.py
```

### Running in Development Mode

For development with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Database

The application uses SQLite by default. The database file (`stories.db`) will be created automatically when you first run the application.

To use a different database, update the `DATABASE_URL` in your `.env` file.

## Environment Variables

- `DATABASE_URL`: Database connection string (default: sqlite:///./stories.db)
- `SECRET_KEY`: Secret key for JWT tokens
- `DEBUG`: Enable debug mode (default: True)
- `ENVIRONMENT`: Environment name (default: development)

## License

This project is open source and available under the MIT License.
