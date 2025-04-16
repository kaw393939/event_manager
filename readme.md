# Event Manager Company: Software QA Analyst/Developer Onboarding Assignment

## Closed Issues and Resolutions 
1. Resolved JWT Token Generation and Test Failure
Updated create_access_token to accept keyword arguments and corrected test fixtures to properly pass payload. Fixed TypeError in API tests.
2.	Mocked Email Service for Test Isolation
Introduced MagicMock to mock email service in tests and avoid real SMTP connections. Fixed SMTPServerDisconnected errors during user creation and registration tests.
3.	Corrected UUID Assertion in Schema Tests
Modified test data to convert UUID to str before assertion to align with expected types in UserResponse schema validation.
4.	Updated Docker Compose and PGAdmin Configs
Verified PGAdmin login credentials from docker-compose.yml environment settings and confirmed PostgreSQL service accessibility via port bindings.
5.	Added Comprehensive Test Coverage for User API
Implemented and refactored multiple test cases covering authentication, user management, and permissions using async_client and role-based JWT tokens.
## Docker Image

This project uses a Docker image built from the provided Dockerfile. The image is built and tagged as:
event_manager-fastapi:latest

You can run this image locally by executing:
docker run -p 8000:8000 event_manager-fastapi:latest

If you need to rebuild the image, run the following command in your project root (where the Dockerfile is located):
docker build -t event_manager-fastapi:latest .

## Reflection
Working on the Event Manager API project has been a valuable learning experience. I deepened my understanding of building secure REST APIs using FastAPI and learned how JWT-based authentication enhances system security. I also recognized the significance of a solid test suite in ensuring code reliability and supporting future development through both manual and automated testing. Addressing challenges related to user profiles, usernames, and passwords further strengthened my ability to design a resilient and well-structured API.