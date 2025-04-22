# Event Manager Company: Software QA Analyst/Developer Onboarding Assignment

Welcome to the Event Manager Company! As a newly hired Software QA Analyst/Developer and a student in software engineering, you are embarking on an exciting journey to contribute to our project aimed at developing a secure, robust REST API that supports JWT token-based OAuth2 authentication. This API serves as the backbone of our user management system and will eventually expand to include features for event management and registration.

---

## Assignment Objectives

1. **Familiarize with REST API functionality and structure**: Gain hands-on experience working with a REST API, understanding its endpoints, request/response formats, and authentication mechanisms.

2. **Implement and refine documentation**: Improve existing documentation based on issues discovered. Ensure it reflects the current codebase accurately.

3. **Engage in manual and automated testing**: Write comprehensive test cases and use automated tools like `pytest` to push test coverage towards 90%. Cover unit, integration, and edge case scenarios.

4. **Explore and debug issues**: Resolve problems related to user profile updates, validation, and OAuth token generation. Log issues clearly and trace them through the application.

5. **Collaborate effectively**: Work with Git for version control and GitHub for code review and issue tracking. Use branches, issues, and pull requests appropriately.

---

## Setup and Preliminary Steps

1. **Fork the Project Repository**  
   Fork [this repository](https://github.com/yourusername/event_manager) to your own GitHub account.

2. **Clone the Forked Repository**  
   ```bash
   git clone https://github.com/yourusername/event_manager.git
   ```

3. **Verify the Project Setup with Docker**  
   Run:
   ```bash
   docker compose up --build
   ```
   Access:
   - API docs: [http://localhost/docs](http://localhost/docs)
   - PGAdmin: [http://localhost:5050](http://localhost:5050)

---

## Testing and Database Management

1. **Explore the API**  
   Use Swagger UI (`http://localhost/docs`) to explore endpoints and test API functionality.

2. **Run Tests with Pytest**  
   Run:
   ```bash
   docker compose exec fastapi pytest
   ```
   Note: This will clear DB tables. You may need to drop Alembic versions manually using PGAdmin.

3. **Increase Test Coverage**  
   Add tests to push the codebase to ~90% coverage. Include edge cases, email validation, password complexity, and profile updates.

---

## Collaborative Development Using Git

1. **Enable Issue Tracking**  
   Enable GitHub Issues to manage bugs and features.

2. **Create Branches for Each Issue**  
   ```bash
   git checkout -b fix-username-validation
   ```

3. **Pull Requests & Code Review**  
   Submit PRs for each issue you fix. Link them to the issue and request review.

---

## Specific Issues Addressed

✅ **Username Validation**  
✅ **Password Validation**  
✅ **Profile Field Edge Cases**  
✅ **Email Update Logic**  
✅ **Validation via Pydantic**  
✅ **Issue from Instructor Video (Email not saving on update)**

Each issue includes:
- Linked test
- Corresponding service/schema/model fix
- Closed GitHub Issue

---

## Docker Container

This project is also available as a prebuilt Docker image:

🧱 **DockerHub Image**: [`jmullen029/event_manager`](https://hub.docker.com/r/jmullen029/event_manager)

Use it to spin up the entire API stack with:

```bash
docker pull jmullen029/event_manager
```

---

## Submission Requirements

- ✅ GitHub repository with:
  - 5 closed issues (username, password, profile edge cases, instructor bug, validation)
  - Corresponding test code and updated logic
  - All merged into `main`

- ✅ Updated README with:
  - 🔗 Links to issues
  - 📦 DockerHub container: [`jmullen029/event_manager`](https://hub.docker.com/r/jmullen029/event_manager)
  - ✍️ 2-3 paragraph reflection below

---

## Reflection

Working on this project has been incredibly valuable for strengthening my backend development and QA skills. I gained hands-on experience with testing REST APIs, debugging real-world issues, and writing resilient validation logic using Pydantic and SQLAlchemy.

The debugging process helped me develop a deeper understanding of how FastAPI interacts with schemas and database models. I also learned the importance of using tools like Swagger and Pytest together to verify and validate functionality. On the collaborative side, working with GitHub Issues, PRs, and branching workflows prepared me for production environments where clean commits and readable code reviews are critical. This was a real growth opportunity and I'm proud of the contributions made.

---

## Resources & Docs

- [Introduction to REST API with Postgres](https://youtu.be/dgMCSND2FQw)  
- [Assignment Instructions](https://youtu.be/TFblm7QrF6o)  
- [Git Cheat Sheet](git.md)  
- [Docker Setup Guide](docker.md)  

**Key Code References**  
- [`tests/conftest.py`](https://github.com/kaw393939/event_manager/commit/3d5802c267036ed410cc7e824f084bdb37ddc8e1) – Fixtures for async DB, tokens  
- [`app/routers/user_routes.py`](https://github.com/kaw393939/event_manager/commit/aae3dfb27df503fef51f435b99c7683b35d44ac7) – User API logic  
- [`app/services/user_service.py`](https://github.com/kaw393939/event_manager/commit/aae3dfb27df503fef51f435b99c7683b35d44ac7) – Core business logic  
- [`app/schemas/user_schemas.py`](https://github.com/kaw393939/event_manager/commit/aae3dfb27df503fef51f435b99c7683b35d44ac7) – Pydantic schemas  
- [`alembic/versions/`](https://github.com/kaw393939/event_manager/commit/aae3dfb27df503fef51f435b99c7683b35d44ac7) – DB migrations

---

**API Docs**: [http://localhost/docs](http://localhost/docs)  
**PGAdmin**: [http://localhost:5050](http://localhost:5050)

---

Thanks for reviewing this assignment.