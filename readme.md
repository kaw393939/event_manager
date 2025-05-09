# 🚀 Event Manager - REST API with JWT Authentication

This project is a secure, robust REST API for user management, built with **FastAPI**, **SQLAlchemy**, and **OAuth2 with JWT tokens**. It also supports event registration and profile management.

## 📦 Project Setup

### 🐳 Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Diya-0816/event_manager.git
   cd event_manager
   ```

2. Create `.env` from sample:

   ```bash
   cp .env.sample .env
   ```

3. Run the containers:

   ```bash
   docker-compose up --build
   ```

4. Access:
   - API Docs: [http://localhost/docs](http://localhost/docs)
   - PGAdmin: [http://localhost:5050](http://localhost:5050)

### 🧪 Run Tests

Tests are written using `pytest`. You can run them with:

```bash
pytest --cov
```

> ⚠️ Running tests will reset the database schema.

## ✅ Closed Issues

Below are the issues resolved as part of this assignment:

| Feature                             | Issue / PR Link                                               | Summary                                                   |
| ----------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------- |
| Username Validation                 | [#256](https://github.com/kaw393939/event_manager/pull/256)   | Fixed username rules, added validation tests              |
| Password Validation                 | [#257](https://github.com/kaw393939/event_manager/pull/257)   | Enforced strong password constraints, added hashing tests |
| Profile Update Edge Case 1          | [#258](https://github.com/kaw393939/event_manager/pull/258)   | Handled simultaneous profile picture and bio updates      |
| Profile Update Edge Case 2          | [#259](https://github.com/kaw393939/event_manager/issues/259) | Managed missing fields and fallback defaults              |
| Instructor Video Issue Fix          | [#260](https://github.com/kaw393939/event_manager/pull/260)   | Resolved OAuth token refresh bug                          |
| Final Cleanup & Refactor Test cases | [#261](https://github.com/kaw393939/event_manager/pull/261)   | Code clean-up and test structure improvements             |

---

## 📚 Reflection

Working on the Event Manager Company assignment helped me understand how to build and test a secure REST API using FastAPI, SQLAlchemy, and JWT-based authentication. I fixed issues related to username and password validation, handled profile update edge cases, and resolved the bug shown in the instructor video. These tasks gave me practical experience with API request validation, secure login flows, and real-world debugging.

I also wrote automated tests using pytest and pushed test coverage over 90%. Creating test cases for login, profile updates, and permission checks improved my confidence in maintaining code quality. Using GitHub for issues, branches, and pull requests helped me follow proper collaboration practices. Overall, this project improved both my technical and teamwork skills.

---

## 🐳 DockerHub Image

[View DockerHub Image](https://hub.docker.com/r/diya0816/event_manager)
