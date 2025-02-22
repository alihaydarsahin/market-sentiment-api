#!/bin/bash

# Stop any running containers
docker-compose down

# Build and start containers
docker-compose up --build -d

# Wait for database to be ready
sleep 10

# Run database migrations
docker-compose exec api flask db upgrade

# Initialize database
docker-compose exec api python src/scripts/create_db.py

# Train models
docker-compose exec api python src/scripts/train_models.py

echo "Deployment complete!" 