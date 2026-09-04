# FastAPI in the Project

## 1. What Is FastAPI

FastAPI is a Python framework for creating web APIs. It accepts HTTP requests, validates input data, calls the required function, and returns a response to the client.

In this project, FastAPI is used as the backend for working with job applications.

General request path:

```text
Client or Swagger
    -> HTTP request
    -> FastAPI
    -> router
    -> endpoint function
    -> SQLAlchemy and database
    -> HTTP response
```

## 2. Starting the Application

From the project root:

```powershell
cd C:\Users\user\Documents\Project
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

## 3. The Main `FastAPI` Object

The application is created in `app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Job Application Automation Platform",
)
```

`app` is the main application object. Routes and startup events are connected through it.
`settings` is the settings object from `app/core/config.py`; `settings.app_name` supplies the application name from the configuration.

Parameters:

- `title` — API name in Swagger;
- `version` — API version;
- `description` — project description.

## 4. Endpoint

An endpoint is a function associated with an HTTP method and URL.

Example in `app/main.py`:

```python
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
    }
```

Here:

- `@app.get("/")` means a GET request at `/`;
- `root` is the function that will be called;
- the returned dictionary is automatically converted to JSON.

## 5. HTTP Methods

The application API uses:

```text
GET   /applications              get all applications
GET   /applications/{id}         get one application
POST  /applications              create an application
PATCH /applications/{id}         update an application
```

### GET

GET is used to read data:

```python
@router.get("")
def list_applications(db: Session = Depends(get_db)):
    ...
```

### POST

POST is used to create data:

```python
@router.post("")
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
):
    ...
```

`payload` contains the JSON sent by the client.
It is an `ApplicationCreate` schema object already validated by Pydantic.

### PATCH

PATCH is used to partially update an existing record:

```python
@router.patch("/{application_id}")
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
):
    ...
```

## 6. `APIRouter`

A router is used to group related endpoints:

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)
```
`prefix` sets the shared URL `/applications`, while `tags` groups these endpoints in Swagger under `applications`.

`prefix` is the shared prefix added to every route.

Therefore:

```python
@router.get("")
```

becomes:

```text
GET /applications
```

And:

```python
@router.get("/{application_id}")
```

becomes:

```text
GET /applications/{application_id}
```

The router is connected in `main.py`:

```python
app.include_router(applications_router)
```

## 7. Pydantic Schemas and Data Validation

Input data is defined in `app/schemas/application.py`:

```python
class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    status: str = "new"
    source: str = "telegram"
```

FastAPI automatically validates JSON before starting the endpoint.

Example of a valid request:

```json
{
  "company": "Google",
  "position": "Python Developer",
  "url": "https://example.com/vacancy",
  "description": "Backend development",
  "status": "new",
  "source": "manual"
}
```

If a required field is missing or empty, FastAPI returns a `422 Unprocessable Entity` error.

## 8. Creating an Application through the API

Function:

```python
@router.post("")
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
):
    application = Application(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Application created",
        "application": application,
    }
```

Here, `db.add()` adds the object to the current session, `db.commit()` commits the transaction and saves the record, and `db.refresh()` rereads the record from the database to obtain the generated `id` and dates.

Workflow:

1. FastAPI receives JSON;
2. Pydantic validates the data;
3. `payload.model_dump()` converts the schema to a dictionary;
4. a SQLAlchemy model is created;
5. the record is added to the database;
6. the API returns a JSON response.

## 9. Dependency Injection and `Depends`

The endpoint contains:

```python
db: Session = Depends(get_db)
```

`Depends` tells FastAPI to obtain a value through `get_db` before calling the function.

`get_db` creates a database session:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI automatically passes `db` to the endpoint and allows the session to be closed after the request.

## 10. Path Parameters

In the route:

```python
@router.get("/{application_id}")
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    ...
```

`application_id` is taken from the URL:

```text
GET /applications/5
```

The value `5` is automatically converted to `int`. If a string is passed instead of a number, FastAPI returns a validation error.

## 11. API Errors

If the application is not found:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail="Application not found",
)
```

The client receives JSON:

```json
{
  "detail": "Application not found"
}
```

Common statuses:

- `200` — successful read or update;
- `201` — resource created when the endpoint is configured for this status;
- `404` — record not found;
- `422` — input data failed validation;
- `500` — internal server error.

## 12. Startup Event

In `main.py`, the application initializes the database at startup:

```python
@app.on_event("startup")
def startup() -> None:
    init_db()
```

Before processing requests, FastAPI calls `init_db`, after which the `applications` table is ready to use.

## 13. Swagger

Swagger is created automatically by FastAPI.

To create an application:

1. open `/docs`;
2. find `POST /applications`;
3. click `Try it out`;
4. paste the JSON;
5. click `Execute`.

Use `GET /applications` to view applications.

## 14. FastAPI and the Rest of the Code

```text
app/main.py
    creates FastAPI and connects routers
        ↓
app/api/routes/applications.py
    accepts HTTP requests
        ↓
app/schemas/application.py
    validates input data
        ↓
app/db/database.py
    provides a Session
        ↓
app/db/models.py
    defines the Application table
        ↓
app.db
    stores data
```

## 15. Glossary

### API

An API is an interface through which one program interacts with another. In this case, the client sends HTTP requests to FastAPI.

Example:

```text
POST /applications
```

### FastAPI

FastAPI is a Python framework that accepts HTTP requests, calls the required functions, and forms responses.

### Endpoint

An endpoint is a specific API function associated with an HTTP method and address.

```python
@router.get("")
def list_applications():
    ...
```

This function handles the `GET /applications` request.

### Router and `APIRouter`

A router is a group of related routes. `APIRouter` creates such an object:

```python
router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)
```

### `prefix`

`prefix` is the shared initial URL fragment for all router routes.

```python
prefix="/applications"
```

Therefore, the route:

```python
@router.get("")
```

gets the full address:

```text
GET /applications
```

And `@router.get("/{application_id}")` becomes `GET /applications/{application_id}`.

### `tags`

`tags` is the name of the endpoint group in Swagger.

```python
tags=["applications"]
```

This is neither a database table nor a URL. The tag is used to group routes conveniently in the documentation.

### Swagger / OpenAPI

Swagger UI is a web page for viewing and testing an API. In FastAPI, it is available at `/docs`.

OpenAPI is a standard description of an API’s routes, parameters, and request and response schemas. FastAPI automatically creates it from Python code and Pydantic models.

Swagger lets you click `Try it out`, fill in JSON, and send a real request to the application.

### ReDoc

ReDoc is an alternative OpenAPI documentation interface. In this project, it is available at `/redoc`.

Swagger is more convenient for manual testing, while ReDoc is often more convenient for reading documentation.

### Pydantic

Pydantic is a library for validating and converting data.

In this project, it is used in `app/schemas/application.py`:

```python
class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1)
```

Pydantic checks that:

- the `company` field exists;
- the value is a string;
- the string contains at least one character.

If the data is invalid, FastAPI does not start the endpoint and returns a `422` error.

### `BaseModel`

`BaseModel` is the Pydantic base class. Input and output data schemas inherit from it.

```python
class ApplicationCreate(BaseModel):
    ...
```

### Schema

A schema describes the shape of the data that the API accepts or returns.

For example, `ApplicationCreate` describes data for creating an application, while `ApplicationUpdate` describes the fields that can be changed.

The Pydantic schema and SQLAlchemy model are different things:

```text
Pydantic schema  → validates HTTP data
SQLAlchemy model → defines the database table
```

### `payload`

`payload` is the variable containing the HTTP request body data.

```python
def create_application(payload: ApplicationCreate):
    ...
```

If the client sends JSON:

```json
{
  "company": "Google",
  "position": "Python Developer"
}
```

FastAPI validates it and passes it to the function as an `ApplicationCreate` object named `payload`.

### Request Body

The request body is the data sent by the client inside an HTTP request. For `POST /applications`, this is JSON containing vacancy information.

### Path Parameter

The path parameter is located directly in the URL:

```python
@router.get("/{application_id}")
```

Request:

```text
GET /applications/5
```

passes the value `application_id = 5` to the function.

### `settings`

`settings` is the application settings object from `app/core/config.py`.

```python
from app.core.config import settings

app_name = settings.app_name
```

The project settings contain:

```python
app_name
environment
database_url
telegram_bot_token
api_base_url
```

Values can be provided by default or read from `.env`.

### `.env`

`.env` is an environment-variable file. It is useful for storing settings that should not be hard-coded in the code.

Example:

```env
DATABASE_URL=sqlite:///./app.db
TELEGRAM_BOT_TOKEN=your_token_here
```

Secret tokens should not be added to Git.

### `Depends`

`Depends` is FastAPI's Dependency Injection mechanism.

```python
db: Session = Depends(get_db)
```

This means: before starting the endpoint, call `get_db` and pass the result to the `db` parameter.

In this case, FastAPI automatically:

1. creates a Session;
2. passes it to the function;
3. closes the Session after the request.

### Dependency Injection

Dependency Injection means passing a ready dependency to a function from outside.

The endpoint does not create the session manually:

```python
def list_applications(db: Session = Depends(get_db)):
    ...
```

FastAPI manages obtaining `db` through `get_db`.

### `Session`

`Session` is a temporary SQLAlchemy work object for reading and changing database data.

```python
db: Session
```

Session is not the database itself and does not retain data after it is closed. Data is saved through `commit()`.

### `db.add()`

`add()` adds an object to the current session:

```python
db.add(application)
```

At this step, the object is prepared for saving, but the transaction has not been committed.

### `db.commit()`

`commit()` commits the transaction and saves changes to `app.db`:

```python
db.commit()
```

Without `commit()`, a new application may not be saved after Session is closed.

### `db.refresh()`

`refresh()` reloads the object from the database:

```python
db.refresh(application)
```

After creation, this provides values assigned by the database:

- `id`;
- `created_at`;
- `updated_at`.

### `db.get()`

`get()` searches for a record by its primary key:

```python
application = db.get(Application, application_id)
```

If the record does not exist, the result is `None`.

### `select()`

`select()` creates a SQLAlchemy read query:

```python
statement = select(Application).order_by(Application.id)
applications = db.scalars(statement).all()
```

`order_by` sets the sort order, `scalars` extracts ORM objects, and `all` gets all results.

### `model_dump()`

`model_dump()` converts a Pydantic object into a regular Python dictionary:

```python
data = payload.model_dump()
application = Application(**data)
```

The `**` operator passes dictionary items as named constructor arguments.

### `exclude_unset=True`

This parameter keeps only fields that the client actually sent:

```python
payload.model_dump(exclude_unset=True)
```

This is important for `PATCH`: if the client changes only `status`, the other fields are not overwritten.

### `HTTPException`

`HTTPException` stops processing and returns an HTTP error to the client:

```python
raise HTTPException(
    status_code=404,
    detail="Application not found",
)
```

### `status_code`

`status_code` is the numeric result of an HTTP request.

The main values in the project are:

- `200` — operation completed;
- `404` — application not found;
- `422` — data failed validation;
- `500` — server error.

### JSON

JSON is a text format for exchanging data between a client and an API.

Python dictionary:

```python
{"company": "Google"}
```

is sent to the client as JSON:

```json
{"company": "Google"}
```

### ORM

ORM stands for Object-Relational Mapping.

Instead of writing SQL manually, we work with an object:

```python
application = Application(...)
```

SQLAlchemy links it to the `applications` table.

### `startup`

`startup` is a FastAPI startup event:

```python
@app.on_event("startup")
def startup() -> None:
    init_db()
```

Before requests are processed, `init_db` is called to create missing tables.

### `uvicorn`

Uvicorn is an ASGI server that runs a FastAPI application:

```powershell
python -m uvicorn app.main:app --reload
```

In `app.main:app`:

- `app.main` — the Python module `app/main.py`;
- `app` — the FastAPI object inside this module.

The `--reload` flag restarts the server after code changes and is used during development.

FastAPI handles the HTTP layer. It is not a database and does not store applications by itself.
