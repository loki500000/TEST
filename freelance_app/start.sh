#!/bin/bash

# AI Freelance Search App - Quick Start Script

echo "🚀 AI Freelance Search App - Quick Start"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp ../.env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo ""
    echo "Required:"
    echo "  - GROQ_API_KEY"
    echo "  - SECRET_KEY (generate a random string)"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Ask user for setup method
echo ""
echo "Choose setup method:"
echo "1. Docker (Recommended - includes PostgreSQL and Redis)"
echo "2. Local development (requires PostgreSQL and Redis installed)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo ""
    echo "🐳 Starting with Docker..."
    echo ""

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Build and start containers
    echo "Building Docker images..."
    docker-compose build

    echo ""
    echo "Starting services..."
    docker-compose up -d

    echo ""
    echo "Waiting for services to be healthy..."
    sleep 5

    # Initialize database
    echo "Initializing database..."
    docker-compose exec api python freelance_app/database/init_db.py create
    docker-compose exec api python freelance_app/database/init_db.py seed

    echo ""
    echo "✅ Application started successfully!"
    echo ""
    echo "📝 Access points:"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs (Swagger): http://localhost:8000/docs"
    echo "  - API Docs (ReDoc): http://localhost:8000/redoc"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "📋 Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop: docker-compose down"
    echo "  - Restart: docker-compose restart"
    echo ""

elif [ "$choice" == "2" ]; then
    echo ""
    echo "💻 Setting up local development environment..."
    echo ""

    # Check Python version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Python version: $python_version"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt

    # Check if PostgreSQL is running
    if ! pg_isready -h localhost -p 5432 &> /dev/null; then
        echo "⚠️  PostgreSQL is not running on localhost:5432"
        echo "Please start PostgreSQL and create a database named 'freelance_db'"
        read -p "Press Enter when PostgreSQL is ready..."
    fi

    # Initialize database
    echo "Initializing database..."
    python database/init_db.py create
    python database/init_db.py seed

    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To start the application:"
    echo "  source venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "Or run with uvicorn directly:"
    echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""

else
    echo "Invalid choice. Exiting."
    exit 1
fi
