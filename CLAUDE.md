# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the Selo v2 Backend - a Django REST API server for speech analysis mobile application. The system focuses on voice recording analysis, user management, and statistical tracking for speech improvement services.

## Project Structure

### Backend Only Architecture

This repository contains only the **Django Backend** component, which was previously located in the BE/ directory. The frontend and AI components have been moved to separate repositories.

### Django Application Structure

Django project structured into focused apps:

- **users/** - User authentication and profile management with custom User model
- **seloing/** - Core speech recording and analysis features  
- **stats/** - User statistics and performance tracking
- **tips/** - Learning content and recommendations
- **medias/** - File upload and media handling
- **common/** - Shared models and utilities

Key architectural patterns:
- Custom User model extending AbstractUser with gender/language/currency choices
- CommonModel base class for shared model fields
- Django REST Framework with token authentication
- CORS headers configured for mobile client

### External Components (Separate Repositories)

- **Frontend**: React Native mobile application (moved to separate repository)
- **AI Services**: Speech analysis and machine learning components (moved to separate repository)

## Development Commands

### Backend (Django)

```bash
# Install dependencies (Poetry required)
poetry install
poetry shell

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Update existing statistics (if needed)
python manage.py update_existing_stats --reset
```

### External Services

Frontend and AI services are maintained in separate repositories.

## Technology Stack

### Backend Technologies
- **Django 5.2.4** with Django REST Framework
- **Poetry** for dependency management (Python 3.13+)
- **SQLite** for development database (PostgreSQL for production)
- **django-cors-headers** for mobile API access
- **python-dotenv** for environment variables
- **PyJWT** for JWT token authentication
- **Gunicorn** for production WSGI server
- **Docker** for containerization

## API Architecture

### Authentication System
- **Token Authentication**: DRF built-in token system
- **JWT Authentication**: Custom JWT implementation for mobile apps
- **Social Login**: Kakao OAuth 2.0 integration
- **User Management**: Custom User model with profile features

### Speech Analysis Flow
1. **Topic Generation** → **Recording Session** → **AI Analysis Request**
2. **Asynchronous Processing** → **Result Callback** → **Statistics Update**
3. Real-time progress tracking and result storage

### Statistics System
- **Auto Statistics**: Automatic updates on seloing completion
- **Conditional Global Stats**: Users with 3+ seloings included in global rankings
- **Performance Tracking**: Score averages, improvement metrics
- **Admin Tools**: Management commands for data migration

## Development Environment

### Prerequisites
- **Python 3.13+** with Poetry
- **Docker & Docker Compose** for containerized deployment
- **PostgreSQL** for production database
- **Redis** for caching (optional)

### Environment Setup
```bash
# Development
poetry install
poetry shell
python manage.py migrate
python manage.py runserver

# Production
docker-compose up -d --build
```

## Code Patterns

### Django Architecture
- **Apps Structure**: Modular Django apps with clear responsibilities
- **Custom Models**: User, Seloing, Statistics with relationship management
- **API Views**: Class-based APIView with proper permission handling
- **Admin Interface**: Comprehensive admin panels with inline editing
- **Signal Handlers**: Auto-creation of related objects and statistics updates

### Security & Deployment
- **Environment Variables**: Secure configuration management
- **CORS Configuration**: Mobile app integration support
- **Rate Limiting**: API endpoint protection via Nginx
- **SSL/TLS**: Cloudflare integration for secure connections