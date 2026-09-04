# SQLAlchemy in the Project

## 1. What Is SQLAlchemy

SQLAlchemy is a library for connecting a Python application to relational databases.

In this project, it connects:

```text
Python Application class
        ↕
applications table in SQLite
```

This approach is called ORM: Object-Relational Mapping.

ORM lets us work with tables through Python objects, while SQLAlchemy generates SQL queries automatically.

## 2. Objects Used

The project has these main objects:

```text
engine       database connection
Base         common model class
Application  applications table model
Session      working database session
sessionmaker session factory
select       SELECT query builder
```

## 3. Installation

The dependency was added to `requirements.txt`:

```text
sqlalchemy==2.0.36
```

Installation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Database URL

In `app/core/config.py`:

```python
database_url: str = "sqlite:///./app.db"
```

SQLAlchemy uses this address to create the connection.

Breakdown:

- `sqlite` — the database dialect;
- `./app.db` — the file path;
- `app.db` — the SQLite file in the project root.

Other databases use different URLs. For example, PostgreSQL:

```text
postgresql+psycopg://user:password@localhost:5432/job_applications
```

When changing databases, the URL and driver usually change, while the models and CRUD code remain.

## 5. `create_engine`

The engine is created in `app/db/database.py`:

```python
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)
```

`engine` is an object that knows:

- the database type;
- the database address;
- how to create connections;
- driver interaction settings.

`engine` does not perform application business logic. It provides technical access to the database.

## 6. `connect_args`

For SQLite, use:

```python
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
```

SQLite normally restricts one connection to one thread. A web application can process requests in different threads, so this restriction is disabled.

This parameter is usually not needed for PostgreSQL.

## 7. `DeclarativeBase` and `Base`

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

`Base` is the common base class for ORM models.

The table model inherits from it:

```python
class Application(Base):
    ...
```

SQLAlchemy registers this model in:

```python
Base.metadata
```

`metadata` contains descriptions of tables, columns, types, and constraints. It does not contain the applications themselves.

## 8. SQLAlchemy Model — a Python Class Connected to a Database Table

In `app/db/models.py`:

```python
class Application(Base):
    __tablename__ = "applications"
```

`__tablename__` sets the table name. `Base` connects this class to the SQLAlchemy ORM.

### `id` Column: `Mapped` Is the Python Type, `mapped_column` Describes the Column

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

`Mapped[int]` means that the field is an integer in Python. `mapped_column(...)` describes how the field is stored in the database. `primary_key=True` makes `id` the primary key that identifies the application.

### String Columns: `String` Is a Length-Limited String

```python
company: Mapped[str] = mapped_column(String(255))
position: Mapped[str] = mapped_column(String(255))
url: Mapped[str] = mapped_column(String(2048))
```

`Mapped[str]` provides the Python type, `mapped_column` connects the attribute to the column, and `String(255)` limits the string to 255 characters. `String(2048)` is used for the URL.

### Long Text: `Text` Is a String Without a Short Length Limit

```python
description: Mapped[str] = mapped_column(Text)
```

`Text` is used for descriptions whose length is not known in advance. Unlike `String(255)`, it does not set a short length limit.

### Default Values

```python
status: Mapped[str] = mapped_column(
    String(50),
    default="new",
)
```

If no status is provided, the ORM uses `new`.

```python
source: Mapped[str] = mapped_column(
    String(50),
    default="telegram",
)
```

The default source is `telegram`.

### Dates: `DateTime` Is the Date and Time, `func.now()` Is the Database's Current Time

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
)
```

`DateTime(timezone=True)` stores the date and time with time-zone support. `server_default=func.now()` means the database itself sets the current time when creating the record.

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
)
```

`onupdate=func.now()` updates the time when the record changes. `func.now()` is SQLAlchemy's representation of the SQL current-time function.

## 9. `Base.metadata.create_all`

In `database.py`:

```python
def init_db() -> None:
    from app.db.models import Application

    Base.metadata.create_all(bind=engine)
```

What happens:

1. the `Application` model is imported;
2. the model is registered in `Base.metadata`;
3. SQLAlchemy checks existing tables;
4. the missing `applications` table is created.

`create_all` does not delete existing data. However, it is not a full migration system: an existing table must be changed through Alembic or separate SQL.

## 10. `sessionmaker`

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
```

`SessionLocal` is a factory for `Session` objects.

Each call:

```python
db = SessionLocal()
```

creates a new session.

Parameters:

- `bind=engine` — work through the created engine;
- `autocommit=False` — save changes only after `commit()`;
- `autoflush=False` — do not send changes automatically before each query.

## 11. `Session`

`Session` is a temporary work context for database operations.

It can:

- execute SELECT;
- add objects;
- update objects;
- delete objects;
- commit transactions;
- roll back transactions.

The session is not the database itself and does not retain data after it closes. Data is saved through `commit()`.

## 12. `get_db`

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Order:

1. a Session is created;
2. the Session is passed to the endpoint;
3. the endpoint performs operations;
4. the Session is closed.

In FastAPI, it is connected through a dependency:

```python
db: Session = Depends(get_db)
```

## 13. `add` — Add an Object to the Current Session

```python
application = Application(**payload.model_dump())
db.add(application)
```

The object is prepared for saving, but the transaction has not been committed.

## 14. `commit` — Commit the Transaction and Save Changes

```python
db.commit()
```

Changes are written to `app.db` only after the transaction is committed.

Creating an application:

```python
db.add(application)
db.commit()
```

If only `add` is called and the session is then closed without `commit`, the record should not be considered saved.

## 15. `refresh` — Reload an Object from the Database

```python
db.refresh(application)
```

After saving, the object is loaded from the database again.

This is needed after creation to obtain values generated by the database:

- `id`;
- `created_at`;
- `updated_at`.

Full sequence:

```python
db.add(application)
db.commit()
db.refresh(application)
```

## 16. `get` — Find an Object by Primary Key

```python
application = db.get(Application, application_id)
```

The search is performed by the primary key `id`.

Example:

```python
application = db.get(Application, 1)
```

This corresponds to the meaning of the query:

```sql
SELECT * FROM applications WHERE id = 1;
```

If the record is not found, the result is `None`.

## 17. `select` — Build a Read Query

```python
from sqlalchemy import select

statement = select(Application).order_by(Application.id)
applications = db.scalars(statement).all()
```

The query is built, but by itself it does not yet return results.

`order_by(Application.id)` sorts the result by identifier.

`db.scalars(statement)` executes the query and extracts ORM objects from the result.

`all()` gets all results as a Python list.

## 18. Updating an Object

In `applications.py`:

```python
for field, value in payload.model_dump(exclude_unset=True).items():
    if value is not None:
        setattr(application, field, value)
```

`setattr` changes a field on the ORM object.

After the update, run:

```python
db.commit()
db.refresh(application)
```

PATCH example:

```json
{
  "status": "interview"
}
```

Only the status changes.

## 19. Transactions and `rollback`

A transaction is a group of changes committed as a whole.

If an error occurs, the changes can be canceled:

```python
try:
    db.add(application)
    db.commit()
except Exception:
    db.rollback()
    raise
```

`rollback()` returns the database to its state before the incomplete transaction.

`close()` closes the session, but does not replace `commit()` or `rollback()` by itself.

## 20. SQLAlchemy and the API

```text
FastAPI endpoint
    -> Depends(get_db)
    -> Session
    -> Application model
    -> SQLAlchemy operation
    -> SQLite app.db
```

Creating an application:

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
    return application
```

Getting applications:

```python
@router.get("")
def list_applications(db: Session = Depends(get_db)):
    statement = select(Application).order_by(Application.id)
    return {"applications": db.scalars(statement).all()}
```

## 21. Process for Adding a New Table

1. Add the library or driver to `requirements.txt`.
2. Add the database URL to `config.py` or `.env`.
3. Use the shared `Base` from `database.py`.
4. Create a new model in `models.py`.
5. Ensure that the model is imported before `create_all`.
6. Create Pydantic schemas for input and output data.
7. Add the endpoint to the router.
8. Obtain a `Session` through `Depends(get_db)`.
9. Implement `select`, `add`, `commit`, `get`, or other operations.
10. Check the API through Swagger.

## 22. SQLAlchemy and Migrations

`create_all` is suitable for initially creating tables. If a table already exists and a column must be added, Alembic is a better choice.

Example model change:

```python
salary: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

Changing the Python class alone will not automatically change an existing table in every environment. Migrations are used for controlled schema changes.

## 23. Final Diagram

```text
config.py
    database_url
        ↓
database.py
    engine, Base, SessionLocal, get_db
        ↓
models.py
    Application and table columns
        ↓
applications.py
    select, add, get, commit, refresh
        ↓
app.db
    saved applications
```
