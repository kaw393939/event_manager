```md
# Event Manager User Management API

This repository contains the backend for an **Event Management Company's user management system**, built as part of an onboarding assignment. The API is developed using **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, with **JWT-based OAuth2 authentication**, **email verification**, and **comprehensive testing**.

## Project Overview

The Event Manager User Management API provides endpoints for **user registration, authentication, profile management, and administration**. Key features include:

- User registration with **email verification**.
- Role-based access control (**ADMIN, MANAGER, AUTHENTICATED**).
- Profile management (**bio, profile picture, social links**).
- Robust validation for **usernames and passwords**.
- Comprehensive **test suite with 90% coverage**.

---

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

- **Docker** and **Docker Compose**
- **Git**

### Running the Application

Clone the repository:

```sh
git clone https://github.com/Raz2997/event_manager.git
cd event_manager
```

Start the services using Docker Compose:

```sh
docker-compose up -d
```

Apply database migrations:

```sh
docker-compose exec fastapi alembic upgrade head
```

### Access the API

- **Swagger UI**: [http://localhost/docs](http://localhost/docs)
- **PGAdmin**: [http://localhost:5050](http://localhost:5050)  
  *(email: `admin@example.com`, password: `adminpassword`)*

---

## Running Tests

Run the test suite with coverage report:

```sh
docker-compose exec fastapi pytest --cov=app --cov-report=html
```

View the coverage report at `htmlcov/index.html`.

---

## Assignment Deliverables

### Implemented Issues

The following issues were addressed to enhance the API’s functionality and security:

- **Username Validation**: Added validation for nickname to enforce maximum length (**50 characters**) and prevent reserved words (**e.g., "admin"**). *Issue #1*
- **Password Validation**: Implemented password complexity rules (**minimum 8 characters, uppercase, lowercase, digit, special character**). *Issue #2*
- **Profile Field Edge Cases**: Ensured robust handling of partial updates for **bio and profile_picture_url**, including validation for invalid URLs. *Issue #3*
- **Username Edge Case**: Prevented nicknames with **leading/trailing hyphens or underscores** using a refined regex. *Issue #4*
- **Common Password Validation**: Added checks to reject **common passwords** (e.g., `"password123"`) for enhanced security. *Issue #5*
- **Instructor Video Issue**: *[Pending clarification; placeholder for sixth issue]*. *Issue #6*

---

## Test Coverage

Achieved **90% test coverage** using pytest, with tests covering:

- **Schema validation** (`tests/test_user_schemas.py`)
- **API endpoints** (`tests/test_users_api.py`)
- **Database operations** (`tests/test_user_model.py`)
- **Security utilities** (`tests/test_security.py`)
- **Email service** (`tests/test_email.py`)

---

## DockerHub

The Docker image for the application is available at:  
🔗 [DockerHub Repository](https://hub.docker.com/r/raz2997/event_manager)

---

## Git Collaboration

### Repository

🔗 [GitHub Repository](https://github.com/Raz2997/event_manager)

### Workflow

- Created **issues** for each task in the GitHub repository.
- Used **feature branches** (e.g., `feature/username-validation`) for development.
- Submitted **pull requests** with detailed descriptions and linked to corresponding issues.

---

## Reflection

This project was a significant learning experience in developing and testing a **secure REST API with FastAPI**. Implementing **username and password validation** deepened my understanding of balancing **security with user experience**, while handling **profile field edge cases** honed my ability to anticipate real-world scenarios.

Achieving **90% test coverage** with **pytest** was challenging but rewarding, emphasizing the importance of **test-driven development**. Collaborating via **Git and GitHub** improved my skills in **branching, pull requests, and code reviews**, preparing me for **team-based workflows**.

Troubleshooting **Docker issues**, such as connection errors on **Windows**, and debugging **database migrations** enhanced my problem-solving abilities. This assignment has equipped me with **practical skills in QA and backend development**, and I’m excited to apply them to future projects.

---
```

