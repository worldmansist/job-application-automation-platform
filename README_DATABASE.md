# How the Database Connection Works

This file explains the SQLite and SQLAlchemy connection in the project in simple steps.

## 1. Before Connecting the Database

Initially, applications were stored in a regular Python list:

```python
applications = []
```

When an application was created, the object was added to this list. The problem is that the list exists only while the Python process is running. After restarting FastAPI, all applications disappeared.

Now the data follows this path:

```text
HTTP request
    -> FastAPI
    -> SQLAlchemy Session
    -> Application model
    -> applications table
    -> app.db file
```

The `app.db` file is the project's local SQLite database.

## 2. Libraries Involved

### FastAPI

FastAPI accepts HTTP requests and calls functions from `app/api/routes/applications.py`.

The project uses these routes:

```text
GET   /applications
GET   /applications/{application_id}
POST  /applications
PATCH /applications/{application_id}
```

FastAPI also validates input data through the Pydantic schemas in `app/schemas/application.py`.

### SQLAlchemy

SQLAlchemy connects Python classes to database tables.

Instead of writing SQL manually, we work with Python objects:

```python
application = Application(**payload.model_dump())
db.add(application)
db.commit()
```

SQLAlchemy converts these operations into SQL queries for SQLite.

### SQLite

SQLite is the database itself. In this case, it is stored in one file:

```text
app.db
```

This is convenient for initial development: there is no need to install a separate PostgreSQL server.

### Pydantic Settings

`pydantic-settings` reads application settings from environment variables and the `.env` file.

This means the database address does not need to be hard-coded in every file.

## 3. Order of Changes

Changes should be made from the bottom up along the dependency chain:

```text
1. requirements.txt  - install the library
2. config.py         - add the database address
3. database.py       - create engine and Session
4. models.py         - define the tables
5. main.py           - create tables at startup
6. applications.py   - use the database in the API
7. Check             - create and read an application
```

This order matters: the router cannot import a model that does not exist yet, and the model cannot connect without `engine` and settings.

## 4. The `requirements.txt` File

The following line was added:

```text
sqlalchemy==2.0.36
```

It installs a fixed version of SQLAlchemy.

After changing dependencies, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Using Python from `.venv` ensures that the library is installed into the project environment.

## 5. The `app/core/config.py` File

The following setting was added:

```python
database_url: str = "sqlite:///./app.db"
```

This is the database address.

Value breakdown:

- `sqlite` — the database type in use;
- `./app.db` — the file in the project's current working directory;
- `database_url` — the Python setting name;
- `DATABASE_URL` — the corresponding variable name in `.env`.

You can create `.env` in the project root:

```env
DATABASE_URL=sqlite:///./app.db
```

If the variable is not specified, the default value from `config.py` is used.

SQLite can later be replaced with PostgreSQL by changing only the address and installing the PostgreSQL driver. The routers will remain almost the same.

## 6. The `app/db/database.py` File

This file is the shared database connection point.

### `Base`

```python
class Base(DeclarativeBase):
    pass
```

`Base` is the common parent of SQLAlchemy models. All models that inherit from it are added to the metadata:

```python
Base.metadata
```

SQLAlchemy uses this metadata to determine which tables need to be created.

### `connect_args`

```python
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
```

SQLite restricts the use of connections from different threads. FastAPI can process requests in different threads, so `check_same_thread=False` is passed for SQLite.

This setting is not needed for PostgreSQL, so an empty dictionary is passed.

### `engine`

```python
engine = create_engine(
    settings.database_url,
    connect_args=connect_args
)
```

`engine` knows where the database is and how to connect to it. It is not a particular application or session.

### `SessionLocal`

```python
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
```

`sessionmaker` is a session factory. Each call creates a separate work object:

```python
db = SessionLocal()
```

Parameters:

- `bind=engine` — the session works through our `engine`;
- `autocommit=False` — changes must be committed with `db.commit()`;
- `autoflush=False` — SQLAlchemy does not automatically send accumulated changes before each query.

### `get_db`

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

The function creates a session, passes it to the FastAPI handler, and closes it after the request finishes.

`yield` lets FastAPI receive the `db` object temporarily.

The session is not the database. It is a temporary work context for database operations.

### `init_db`

```python
def init_db() -> None:
    from app.db.models import Application

    Base.metadata.create_all(bind=engine)
```

`create_all` creates tables that do not exist yet.

The `Application` import inside the function ensures that the model is registered in `Base.metadata` before `create_all` is called.

## 7. The `app/db/models.py` File

The model describes a database table:

```python
class Application(Base):
    __tablename__ = "applications"
```

This means that the `Application` class is connected to the `applications` table.

### Model Fields

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

The application's primary key. SQLite automatically assigns new `id` values.

```python
company: Mapped[str] = mapped_column(String(255))
position: Mapped[str] = mapped_column(String(255))
url: Mapped[str] = mapped_column(String(2048))
```

Text fields for the company, position, and link.

```python
description: Mapped[str] = mapped_column(Text)
```

Long vacancy description.

```python
status: Mapped[str] = mapped_column(String(50), default="new")
source: Mapped[str] = mapped_column(String(50), default="telegram")
```

The application's status and source. If values are not provided, the default values are used.

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
)
```

The creation date is set by the database.

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now()
)
```

The creation date is set when the record is added, while `onupdate` asks SQLAlchemy to update it when the record changes.

Final table:

```text
applications
- id
- company
- position
- url
- description
- status
- source
- created_at
- updated_at
```

## 8. The `app/main.py` File

The following import was added to the main file:

```python
from app.db.database import init_db
```

And the following startup handler:

```python
@app.on_event("startup")
def startup() -> None:
    init_db()
```

When FastAPI starts, `startup` is called, followed by `init_db`.

If `app.db` does not exist yet, SQLite creates it. SQLAlchemy then creates the `applications` table.

This happens automatically at startup:

```powershell
python -m uvicorn app.main:app --reload
```

Important: `create_all` creates missing tables but is not a full migration system. If an existing table needs to be changed, Alembic will be needed later.

## 9. The `app/api/routes/applications.py` File

Here, the API has been switched from a Python list to the database.

### Connecting Dependencies

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Application
```

- `Depends` asks FastAPI to provide a session;
- `Session` is used for the type annotation;
- `select` creates a query;
- `Application` represents the table;
- `get_db` creates and closes the session.

### Getting All Applications

```python
def list_applications(db: Session = Depends(get_db)):
    return {
        "applications": db.scalars(
            select(Application).order_by(Application.id)
        ).all()
    }
```

FastAPI calls `get_db`, receives `db`, and then queries the table.

`scalars` extracts `Application` objects, and `all` converts the result into a list.

### Getting One Application

```python
application = db.get(Application, application_id)
```

The search is performed by the primary key `id`.

If the record does not exist, the API returns:

```python
raise HTTPException(status_code=404, detail="Application not found")
```

### Creating an Application

```python
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db)
):
    application = Application(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
```

Steps:

1. `ApplicationCreate` validates the input JSON;
2. `model_dump()` converts the Pydantic object to a dictionary;
3. `Application(...)` creates a SQLAlchemy model object;
4. `db.add()` adds it to the current transaction;
5. `db.commit()` saves it to SQLite;
6. `db.refresh()` loads the generated `id` and dates.

### Updating an Application

```python
for field, value in payload.model_dump(exclude_unset=True).items():
    if value is not None:
        setattr(application, field, value)
```

`exclude_unset=True` allows only fields included in the request to be changed.

For example:

```json
{
  "status": "interview"
}
```

changes only the status, while the other fields remain unchanged.

After the update, run:

```python
db.commit()
db.refresh(application)
```

## 10. Complete Application Creation Flow

```text
1. The client sends POST /applications
2. FastAPI receives JSON
3. ApplicationCreate validates the data
4. Depends(get_db) creates a Session
5. An Application object is created
6. db.add() adds it to the transaction
7. db.commit() writes it to app.db
8. db.refresh() obtains the id and dates
9. The API returns the application
10. get_db closes the Session
```

After the server restarts, the record remains because it is stored in `app.db`, not in Python memory.

## 11. How to Verify It Works

Start the application from the project root:

```powershell
cd C:\Users\user\Documents\Project
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Create an application through `POST /applications`:

```json
{
  "company": "Google",
  "position": "Python Developer",
  "url": "https://example.com/vacancy",
    "description": "Backend development in Python",
  "status": "new",
  "source": "manual"
}
```

Then run `GET /applications` and verify that the application appears.

Then stop the server with `Ctrl+C`, start it again, and repeat `GET /applications`. The record should remain.

## 12. Important Differences Between Components

```text
config.py       knows the database address
    ↓
database.py     creates engine and Session
    ↓
models.py       defines tables
    ↓
main.py         starts table creation
    ↓
applications.py performs API operations
```

- `engine` knows how to connect to the database;
- `Session` performs specific operations;
- `Application` describes the table structure;
- `db.add`, `db.commit`, and `db.get` work through the session;
- FastAPI connects the HTTP request to the router function.

## 13. What to Do Next

The current version is suitable for the first local stage. Next steps:

1. Add `rollback()` handling for errors.
2. Create tests for all endpoints.
3. Add Alembic for migrations.
4. Add tables for companies, statuses, and change history.
5. Switch SQLite to PostgreSQL when a shared server database becomes necessary.
