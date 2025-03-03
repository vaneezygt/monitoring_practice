# FastAPI Kafka Application

A FastAPI application demonstrating integration with Kafka for message processing and PostgreSQL for data storage.

## Features

- User authentication with JWT
- Message creation and retrieval
- Real-time message processing with Kafka
- PostgreSQL database integration
- Async SQLAlchemy with PostgreSQL
- Docker containerization

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/lazorikv/fastapi-kafka-app.git
cd fastapi-kafka-app
```
1. Create environment file:

```bash
cp .env.example .env
```
1. Build and start the containers:

```bash
docker-compose up --build
```

The application will start using the built-in development server with hot reload enabled.
Access the application at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
First you need to create a user:
- `POST /api/v1/users/` - Create new user

Then you can get a JWT token:
- `POST /api/v1/auth/token` - Get JWT token (login)

### Users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/{user_id}` - Get user details
- `DELETE /api/v1/users/{user_id}` - Delete user

### Messages
- `POST /api/v1/messages/` - Create new message
- `GET /api/v1/messages/` - List all messages
- `GET /api/v1/messages/{message_id}` - Get message details

## Development

To run database migrations:

```bash
docker-compose exec app alembic upgrade head
```

To create a new migration:

```bash
docker-compose exec app alembic revision --autogenerate -m "migration message"
```

## Architecture

The application follows a layered architecture:
1. API Layer (FastAPI routes)
2. Service Layer (Business logic)
3. Repository Layer (Database operations)
4. Model Layer (Database models)

Messages flow:
1. Client creates a message via REST API
2. Message is saved to PostgreSQL
3. Message is sent to Kafka topic
4. Kafka consumer processes the message (logging, etc.)
