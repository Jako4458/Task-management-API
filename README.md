# Task-management-API
## API Overview

This project uses Swagger UI for full API documentation, available at `/docs`.

---

### Key Endpoints

#### 🔐 Auth
- `POST /register` – Register a new user
- `POST /login` – Authenticate and receive a JWT token

#### ✅ Tasks (Requires Authentication)
- `GET /tasks` – List tasks for the logged-in user
- `POST /tasks` – Create a new task
- `PUT /tasks/{task_id}` – Update an existing task
- `DELETE /tasks/{task_id}` – Delete a task

---
### Setup

To run the server using Docker you simply have to:
- copy '.env.example' to '.env' and update the variables
- run 'docker-compose build'
- run 'docker-compose up -d'
**Note** If the flask application starts before the Postgres is ready for connection flask will fail and a simple rerun of 'docker-compose up -d' should fix it 
  
### 🧪 Testing Overview

Automated testing is included using **pytest** to verify the API functionality and database behavior.

#### Setup
To setup a testing environment and run the test you must:
- update variables in '.env.testing'
- run a Postgres testing database. Can be done from docker with 'docker-compose --profile testing up -d testing_postgres' and run 
- run either 'pytest' for all tests or 'pytest <filename>' for specific tests.

#### ✅ What’s Tested:
- **User registration**: Valid and invalid cases (missing fields, empty strings)
- **Login flow**: Valid login, wrong credentials, user not found
- **JWT handling**: Valid and invalid tokens
- **Task management**:
  - Inserting a task and verifying its persistence
  - Getting tasks (authenticated only)
  - Input validation (e.g., missing title)

#### 🧱 Test Types:
- **Unit tests** for core database access logic (e.g., `get_user_by_username`, `insert_task`)
- **Integration tests** for full end-to-end flows using `flask.test_client()` and a real database connection

#### 📦 Fixtures:
- Database is re-created per test session using test fixtures
- Auth tokens are generated dynamically for authenticated requests

---

### 📝 Note
Only a representative subset of possible scenarios is tested to demonstrate structure, correctness, and test methodology. Full test coverage would follow the same structure and conventions shown.

## Live Demo

This project can optionally be viewed live via a temporary Cloudflare Tunnel or similar deployment. If enabled, the API will be accessible at:

**🔗 https://taskmanagementapi.jbhyldgaard.dk/docs/**

