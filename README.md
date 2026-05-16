# GameBase API

A Flask REST API for managing games, reviews, developers, genres, authentication, and role-based moderation systems.

Built with Flask, SQLAlchemy, PostgreSQL, JWT authentication, Docker, and deployed on Render.


## Features

- JWT authentication with access and refresh token rotation
- Secure HTTP-only cookie authentication
- Role-based access control (User / Moderator / Admin)
- PostgreSQL database with SQLAlchemy ORM
- Alembic database migrations
- RESTful API architecture
- Pagination, filtering, and sorting
- Incremental rating calculations
- Reporting and moderation system
- Rate limiting with Flask-Limiter
- Dockerized deployment
- Render cloud deployment


## Tech Stack

- Python 3.12
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-JWT-Extended
- Flask-Migrate / Alembic
- Flask-Limiter
- flask-smorest
- Marshmallow
- Pytest
- Docker
- Gunicorn
- Render


## Architecture Notes

- The application uses the Flask application factory pattern.
- Authentication is implemented using JWT access and refresh tokens.
- Access and refresh tokens are stored in HTTP-only cookies for improved security.
- Database schema migrations are handled with Alembic.
- Incremental rating updates are used to avoid looping through every review on every request.
- Role-based authorization separates normal users, moderators, and administrators.
- 160 Pytest tests cover edge cases, authorization rules, moderation policies, and database integrity.


## Environment Variables

Create a .env file based on .env.example inside the GameBaseAPI/ directory.


## Running Locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:

pip install -r requirements.txt

4. Create .env file in GameBaseAPI/ based on .env.example
5. Run database migrations:

flask --app GameBaseAPI.run:app db upgrade

6. Start the server:

python run.py


## Deployment

The application is containerized with Docker and deployed on Render using Gunicorn as the production WSGI server.


## Base URL

Local: http://localhost:5000  
Production: https://games-api-foy4.onrender.com


## API Documentation

Swagger/OpenAPI documentation is available at:

/api/docs

It can also be accessed from the main page through the
"FULL SWAGGER UI DOCUMENTATION" button.


## Key Design Decisions

- Refresh token rotation is implemented to reduce the risk of session hijacking
- HTTP-only cookies are used for authentication to mitigate XSS-related token theft
- CSRF protection is enabled to mitigate CSRF risks associated with cookie-based authentication
ole-based, context-specific access control is used to reduce moderation abuse
- Incremental rating updates to reduce database load
- Database-leve unique constraints to prevent abuse and preserve database integrity


## Future Improvements

- Redis-backed distributed rate limiting
- Caching layer
- WebSockets for live updates