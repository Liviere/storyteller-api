#!/bin/bash
# update_dependencies.sh - Script to update dependencies with priority

echo "🔍 Checking for outdated packages..."
poetry show --outdated

echo ""
echo "🚀 Starting priority updates..."

echo "📦 1. Updating core FastAPI..."
poetry update fastapi

echo "📦 2. Updating SQLAlchemy..."
poetry update sqlalchemy

echo "📦 3. Updating Pydantic (data validation)..."
poetry update pydantic

echo "📦 4. Updating Uvicorn (server)..."
poetry update uvicorn

echo "📦 5. Updating database tools..."
poetry update alembic

echo "📦 6. Updating auth libraries..."
poetry update python-jose passlib

echo "📦 7. Updating utilities..."
poetry update python-dotenv python-multipart

echo "🛠️  8. Updating development tools..."
poetry update black isort flake8 mypy pytest pytest-asyncio httpx

echo ""
echo "✅ All updates completed!"
echo ""
echo "🔍 Final package versions:"
poetry show --latest | head -20
