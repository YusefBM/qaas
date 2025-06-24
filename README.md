# Quiz-as-a-Service (QaaS) - Backend Engineering Assessment

A Django-based Quiz-as-a-Service platform that allows users to create, manage, and participate in quizzes through a REST API. Built with Clean Architecture principles using Domain-Driven Design (DDD) and CQRS patterns.

## Features

### Quiz Creator Functionality
- ✅ Create quizzes with multiple-choice questions
- ✅ Send quiz invitations via email
- ✅ View quiz scores and participant statistics
- ✅ Manage created quizzes
- ✅ Asynchronous email delivery with Celery

### Quiz Participant Functionality
- ✅ Accept quiz invitations
- ✅ Participate in invited quizzes
- ✅ Submit quiz answers
- ✅ View personal quiz results
- ✅ Access quizzes through invitation links

### Admin Interface
- ✅ Comprehensive Django admin interface
- ✅ Manage all quiz-related data
- ✅ User management and permissions

## Technology Stack

- **Backend**: Django 4.2.22
- **API**: Django REST Framework 
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.1)
- **Task Queue**: Celery 5.3.6 with Redis 5.0.1
- **Email**: Django email backend with HTML/text templates
- **Containerization**: Docker & Docker Compose
- **Code Quality**: Black, Flake8
- **Architecture**: Clean Architecture with DDD and CQRS

## Architecture

The project follows **Clean Architecture** principles with:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and command/query handlers (CQRS)
- **Infrastructure Layer**: External services, repositories, and views
- **Domain-Driven Design**: Aggregates, repositories, and domain services
- **Dependency Injection**: Factory pattern for loose coupling

## Getting Started

### Prerequisites
- Docker
- Docker Compose
- Make (for convenience commands)

### Installation & Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd qaas
```

2. **Complete setup with one command:**
```bash
# This will set up everything: environment, build, migrate, and create superuser
make setup-env
```

3. **Start the application:**
```bash
# Start all services (Django, PostgreSQL, Redis, Celery)
make run
```

4. **Access the application:**
   - API Base URL: http://localhost:8000/api/
   - Admin Interface: http://localhost:8000/admin/

### Common Development Commands

```bash
# Stop the application
make stop

# Restart the application
make restart

# Access Django shell
make shell

# Run all tests
make test

# Generate new migrations
make generate-migrations

# Apply specific migration
make migrate app=quiz migration=0001

# View all available commands
make help
```

### Code Quality Commands

```bash
# Run all linting checks (flake8 + black)
make lint

# Format code automatically with black
make format

# Run only flake8 linter
make lint-flake8

# Run only black formatter check
make lint-black
```

## Authentication

The API uses **JWT Authentication** with the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | User registration |
| `/api/auth/login/` | POST | Login and get JWT tokens |
| `/api/auth/refresh/` | POST | Refresh access token |
| `/api/auth/verify/` | POST | Verify token validity |
| `/api/auth/logout/` | POST | Logout and blacklist token |
| `/api/profile/` | GET | Get user profile |

**Token Configuration:**
- Access Token Lifetime: 60 minutes
- Refresh Token Lifetime: 7 days
- Token rotation enabled
- Token blacklisting on logout

For detailed authentication usage, see the [Testing Guide](HOW_TO_TEST.md).

## API Documentation

### Core API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/1.0/quizzes/` | GET | List user's accessible quizzes | ✅ |
| `/api/1.0/quizzes/` | POST | Create a new quiz | ✅ |
| `/api/1.0/quizzes/{quiz_id}/` | GET | Get quiz details | ✅ |
| `/api/1.0/creators/{creator_id}/quizzes/` | GET | Get creator's quizzes | ✅ |
| `/api/1.0/quizzes/{quiz_id}/invitations/` | POST | Send quiz invitation | ✅ |
| `/api/1.0/invitations/{invitation_id}/accept/` | POST | Accept invitation | ✅ |
| `/api/1.0/quizzes/{quiz_id}/submit/` | POST | Submit quiz answers | ✅ |
| `/api/1.0/quizzes/{quiz_id}/scores/` | GET | Get quiz scores (creator only) | ✅ |

For detailed API usage examples, request/response formats, and complete testing workflows, see the [Testing Guide](HOW_TO_TEST.md).

## Testing

The project includes comprehensive tests covering all layers of the Clean Architecture:
- **Domain Layer**: Business logic and rules
- **Application Layer**: Command and query handlers
- **Infrastructure Layer**: Repositories and external services

```bash
# Run all tests
make test
```

For detailed testing instructions, API usage examples, and complete testing workflows, see the [Testing Guide](HOW_TO_TEST.md).

## Development

### Code Quality Tools
- **Black**: Code formatting (line length: 120)
- **Flake8**: Linting and style checking

## Security Features

- **JWT Authentication**: Token-based authentication with rotation
  - Access tokens expire in 60 minutes
  - Refresh tokens expire in 7 days
  - Automatic token rotation and blacklisting
- **Token Blacklisting**: Secure logout functionality with token invalidation
- **Permission Checks**: Proper authorization throughout the application
- **ALLOWED_HOSTS**: Configurable host validation (defaults to "*" in debug mode)
- **UUID Primary Keys**: Non-sequential identifiers for enhanced security
- **Input Validation**: Comprehensive request validation using Voluptuous
- **SQL Injection Protection**: Django ORM built-in protection

## Monitoring and Logging

- **Django Logging**: Configured for development and production
- **Celery Monitoring**: Task execution tracking
- **Database Query Logging**: Performance monitoring
- **Error Handling**: Comprehensive exception handling

## Deployment

### Production Considerations
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS` (remove wildcard "*")
- Use proper secret management (Kubernetes Secrets, HashiCorp Vault, AWS Secrets Manager, etc.)
- Set up health checks and readiness probes

## Additional Documentation

- [Testing Guide](HOW_TO_TEST.md) - Comprehensive testing instructions and examples
- [Architecture Documentation](quiz/tests/README.md) - Technical architecture details
