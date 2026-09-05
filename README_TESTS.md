# Testing Guide

## Why the Project Needs Tests

Tests check that the application behaves as expected after code changes.

For this project, tests will help us verify that:

- the API starts correctly;
- a new application can be created;
- an application can be found by its ID;
- a missing application returns a `404` error;
- an application can be updated;
- invalid input is rejected;
- database data is isolated between tests;
- future bot changes do not break the API contract.

A test is a small program that performs an action and checks the result automatically.

Example:

```text
Send a POST request to create an application
        |
        v
Check that the response status is 200
        |
        v
Check that the response contains an ID
```

## Current State

The first API test suite has been added to the project.

Implemented files and changes:

- `pytest==8.3.3` was added to `requirements.txt`;
- `tests/__init__.py` was created;
- `tests/conftest.py` contains the isolated test database and client fixture;
- `tests/test_applications.py` contains seven API tests;
- application code, Telegram bot code, `.vscode/tasks.json`, and the real `app.db` were not changed for this test suite.

Current result:

```text
7 passed
```

## Tools We Will Use

### pytest

`pytest` is a Python framework for writing and running tests.

It finds files with names such as:

```text
test_*.py
*_test.py
```

It also finds functions whose names start with `test_`.

### FastAPI TestClient

`TestClient` allows us to send requests to the FastAPI application from Python without opening a browser and without manually starting Uvicorn.

With it, a test can send requests such as:

```python
client.get("/health")
client.post("/applications", json=payload)
client.patch("/applications/1", json=payload)
```

### SQLite test database

The application currently uses SQLite. Tests should use a separate temporary database instead of the real `app.db` file.

This is important because tests must not delete or modify the user's development data.

## Test Structure

Later, we will create this structure:

```text
Project/
├── app/
│   ├── main.py
│   ├── api/
│   ├── db/
│   └── schemas/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_applications.py
└── requirements.txt
```

### `tests/__init__.py`

Marks the `tests` folder as a Python package. It can remain empty.

### `tests/conftest.py`

Contains shared test configuration and fixtures.

A fixture is reusable preparation code. For example, it can:

1. create a temporary database;
2. create database tables;
3. create a test client;
4. provide the client to a test;
5. remove the temporary database after the test.

### `tests/test_applications.py`

Contains the first tests for the application API.

The first tests will cover the endpoints in:

- `GET /health`;
- `GET /applications`;
- `POST /applications`;
- `GET /applications/{application_id}`;
- `PATCH /applications/{application_id}`.

## Tests That Are Implemented

### 1. Health check

The test sends a request to `GET /health` and checks that the API confirms that it is running.

### 2. Empty application list

The test uses a new test database and checks that the first request returns an empty list.

### 3. Create an application

The test sends valid JSON:

```json
{
  "company": "Example Company",
  "position": "Python Developer",
  "url": "https://example.com/job",
  "description": "Backend development",
  "status": "new",
  "source": "test"
}
```

Then it checks that:

- the request succeeds;
- the response contains an application;
- the application receives an integer `id`;
- the submitted fields are saved;
- `created_at` and `updated_at` exist.

### 4. Get an application

The test first creates an application and then requests it by ID.

It checks that the returned application has the same data.

### 5. Missing application

The test requests an ID that does not exist.

Expected result:

```text
HTTP status: 404
Detail: Application not found
```

### 6. Update an application

The test changes one or more fields with `PATCH` and checks that the new values are returned.

### 7. Invalid data

The test sends data with an empty required field, for example an empty company name.

Expected result:

```text
HTTP status: 422
```

FastAPI returns `422` when the request does not satisfy the Pydantic schema.

## How to Run Tests

Activate the virtual environment from the project root:

```powershell
.\\.venv\\Scripts\\Activate.ps1
```

If dependencies have not been installed yet, install them with:

```powershell
pip install -r requirements.txt
```

Run the complete test suite from the project root:

```powershell
pytest
```

To see more information about every test:

```powershell
pytest -v
```

To run one file only:

```powershell
pytest tests/test_applications.py -v
```

To run one test by its name:

```powershell
pytest tests/test_applications.py -k create -v
```

The command must be run from:

```text
C:\Users\user\Documents\Project
```

The virtual environment should be active before running the commands:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Successful Result

When all tests pass, `pytest` displays a result similar to:

```text
7 passed
```

The exact number may change when new functionality is added.

If a test fails, pytest shows:

- the test that failed;
- the expected result;
- the actual result;
- the file and line where the assertion failed.

## Important Rules

### Tests must not use the real database

Tests should not work with the existing `app.db` file. Each test run should use a separate test database.

### Tests should be independent

A test must not rely on another test running before it. Every test should prepare the data it needs.

### One test should check one behavior

Small tests are easier to understand and debug.

For example, it is better to have separate tests for:

- creating an application;
- finding an application;
- updating an application;
- handling a missing application.

### Tests should check behavior, not implementation details

A test should check what the user receives from the API. It should not depend unnecessarily on the internal names of local variables or helper functions.

## What Was Done

Testing was added in the following order:

1. Add `pytest` to `requirements.txt`.
2. Create the `tests` folder.
3. Configure a separate in-memory SQLite database.
4. Add a shared test client fixture.
5. Add a test for the health endpoint.
6. Add tests for creating and listing applications.
7. Add tests for getting and updating applications.
8. Add tests for errors and invalid data.
9. Run the complete test suite.

The next tests can cover the Telegram bot and more detailed validation after the API behavior is extended.

## What Is Not Covered Yet

At this stage we are not adding:

- tests for the Telegram bot conversation flow;
- PostgreSQL test containers;
- integration tests with real Telegram;
- performance tests;
- CI/CD test workflows.

Those can be added after the API tests work reliably.
