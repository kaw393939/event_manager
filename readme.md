THIS IS MY ASSIGNMENT-10

Excited to Join Event Manager Company as a Software QA Analyst/Developer!
As a student pursuing software engineering and now part of the Event Manager Company, I’ve begun working on an exciting project focused on building a secure and scalable REST API. This API forms the foundation of our user management system and uses JWT-based OAuth2 authentication for enhanced security. In the future, it will grow to include functionalities like event creation and registration.

SETUP INSTRUCTIONS

STEP 1: Fork the professor’s repository to your own GitHub account.

STEP 2: Clone the forked repository to your local machine to start working on it.

git clone: https://github.com/Mahathma-b5/Homework10.git

STEP 3: Start the application using Docker

docker compose up --build

STEP 4: Access Swagger UI at : localhost/docs

<img width="1440" alt="Screenshot 2025-04-19 at 6 27 21 PM" src="https://github.com/user-attachments/assets/b4fefe7c-67cf-406a-9425-f12f329a80df" />

<img width="1440" alt="Screenshot 2025-04-19 at 6 27 35 PM" src="https://github.com/user-attachments/assets/58287cdf-101c-4fd1-84c3-cced51097598" />

STEP 5: Access PGAdmin at : localhost:5050

<img width="1440" alt="Screenshot 2025-04-19 at 6 29 36 PM" src="https://github.com/user-attachments/assets/475af9da-67cc-4452-a299-3021adf48ad3" />

CLOSED ISSUES AND FIXES 

1-PASSWORD VALIDATION 

To enhance authentication security, we implemented comprehensive password validation that accurately detects incorrect credentials during login attempts and provides clear error feedback to assist users. Additionally, we addressed the issue of weak password acceptance by enforcing strong password policies—requiring a mix of uppercase, lowercase, numbers, and special characters—to prevent unauthorized access. This is further supported by backend validation during user registration to ensure all passwords meet the required complexity standards.

Link to the Issue- https://github.com/Mahathma-b5/Homework10/issues/3

2-TOKEN REQUEST ISSUE

To enhance both usability and security, the login system was updated by replacing traditional username-based authentication with email-based verification. Since email addresses are inherently unique and easier to remember, this change streamlines the login and verification process, making it more intuitive for users. It also eliminates confusion caused by duplicate or forgotten usernames. By leveraging email as the primary identifier, the system ensures more accurate user recognition and delivers a smoother, more efficient authentication experience overall.  

Link to the Issue- https://github.com/Mahathma-b5/Homework10/issues/2

3- LOGIN PAGE ERROR FIX

I noticed that when users entered wrong login info or if their account was locked, the error messages weren’t very clear. So I updated the login logic to show proper messages — like “Incorrect email or password” for invalid attempts and “Account locked” if they’ve tried too many times

Link to the Issue- https://github.com/Mahathma-b5/Homework10/pull/6

4- JWT ACCESS TOKEN EXPIRY

The login authentication previously failed for users with ADMIN and MANAGER roles due to issues in JWT token handling. This was resolved by correcting the token generation and authentication logic to properly recognize and validate user roles during login. Additionally, several Pytest-related errors were fixed to ensure seamless testing of authentication flows and email verification functionalities.

Link to the Issue- https://github.com/Mahathma-b5/Homework10/pull/7

5- URL VERIFICATION

To enhance data integrity and input validation, strict URL checks were implemented to prevent submission of improperly formatted or invalid links. Unit tests were added to verify both valid and invalid URL scenarios. The system now returns clear and descriptive error messages when invalid URLs are detected, ensuring all provided URLs meet standard formatting rules and improving overall reliability.

Link to the Issue- https://github.com/Mahathma-b5/Homework10/pull/8

DOCKER HUB DEPLOYMENT:


<img width="1470" alt="Screenshot 2025-04-19 at 8 51 17 PM" src="https://github.com/user-attachments/assets/1d2a91e1-7741-4c6e-881d-036efe2e8696" />

<img width="1264" alt="Screenshot 2025-04-19 at 8 53 20 PM" src="https://github.com/user-attachments/assets/a6348404-7080-43ec-bd71-b1d4d06130b6" />


TESTING:

<img width="1035" alt="Screenshot 2025-04-19 at 7 39 44 PM" src="https://github.com/user-attachments/assets/1a170a66-0229-4322-a6ef-c11f9ea1c2b5" />


REFLECTIONS:

This project was a valuable opportunity to bridge theoretical knowledge with real-world API development. I deepened my understanding of FastAPI, asynchronous database handling, and Pydantic validation while also improving my debugging and problem-solving skills. Throughout the process, I tackled challenges such as inconsistent data examples, missing validations, and unhandled login errors by implementing standardized data, robust validation logic, clearer error handling, and endpoint security. I also integrated JWT-based authentication, managed database migrations with Alembic, and set up an operational CI/CD pipeline using Docker and GitHub Actions. These hands-on experiences have significantly strengthened my skillset and will be highly beneficial for future collaborative projects and professional development in the industry.

