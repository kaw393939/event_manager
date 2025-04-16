# Event Manager API – QA Assignment Completion

---

## Test Coverage and Quality Assurance (QA)

### Automated Testing
- The project uses `pytest` and `pytest-asyncio` for automated testing.
- Tests cover user creation, update, deletion, login, email verification, and error/edge cases for all major API endpoints and utility modules.
- **Test coverage exceeds 90%** (see below for coverage instructions).

### Running Tests
To run all tests and view coverage:

```bash
docker compose exec fastapi pytest --cov=app --cov-report=term-missing
```

To generate an HTML coverage report:

```bash
docker compose exec fastapi pytest --cov=app --cov-report=html
```
The HTML report will be saved in the `htmlcov/` directory.

### Linting and Formatting
- Code is formatted with [Black](https://black.readthedocs.io/) and follows PEP8 standards.
- Run `black .` and `flake8 .` to check formatting and lint errors.

---

## Reflection & Lessons Learned

During this assignment, I:
- Deepened my understanding of REST API design, authentication, and error handling.
- Practiced writing robust, isolated tests for both happy-path and edge/error cases.
- Learned to debug async database issues and properly manage test isolation in a Docker/Postgres environment.
- Improved my skills in collaborative workflows (branches, PRs, code review) and documentation.

**Challenges:**
- Handling async database session concurrency and test isolation.
- Achieving high test coverage on complex API branches and error paths.

**Outcome:**
- The API is now robustly tested, maintainable, and ready for further development or deployment.
- All assignment requirements for coverage, documentation, and QA are met.

---

## Submission Checklist
- [x] 90%+ test coverage achieved and verified.
- [x] All tests pass in CI and local Docker.
- [x] README updated with coverage, test, and reflection sections.
- [x] All issues/PRs documented and merged.

---
