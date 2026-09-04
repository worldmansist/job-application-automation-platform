# SQLAlchemy в проекте

## 1. Что такое SQLAlchemy

SQLAlchemy — библиотека для работы Python-приложения с реляционными базами данных.

В проекте она связывает:

```text
Python-класс Application
        ↕
таблица applications в SQLite
```

Этот подход называется ORM: Object-Relational Mapping.

ORM позволяет работать с таблицами через Python-объекты, а SQLAlchemy самостоятельно формирует SQL-запросы.

## 2. Какие объекты используются

В проекте есть основные объекты:

```text
engine       подключение к базе
Base         общий класс моделей
Application  модель таблицы applications
Session      рабочая сессия с базой
sessionmaker фабрика сессий
select       построитель SELECT-запросов
```

## 3. Установка

В `requirements.txt` добавлена зависимость:

```text
sqlalchemy==2.0.36
```

Установка:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. URL базы данных

В `app/core/config.py`:

```python
database_url: str = "sqlite:///./app.db"
```

SQLAlchemy использует этот адрес для создания подключения.

Разбор:

- `sqlite` — диалект базы;
- `./app.db` — путь к файлу;
- `app.db` — файл SQLite в корне проекта.

Другие базы используют другие URL. Например, PostgreSQL:

```text
postgresql+psycopg://user:password@localhost:5432/job_applications
```

При смене базы обычно меняются URL и драйвер, а модели и CRUD-код сохраняются.

## 5. `create_engine`

В `app/db/database.py` создаётся engine:

```python
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)
```

`engine` — объект, который знает:

- тип базы;
- адрес базы;
- способ создания подключений;
- настройки взаимодействия с драйвером.

`engine` не выполняет бизнес-логику заявок. Он предоставляет технический доступ к базе.

## 6. `connect_args`

Для SQLite используется:

```python
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
```

SQLite по умолчанию ограничивает использование одного соединения одним потоком. Веб-приложение может обрабатывать запросы в разных потоках, поэтому ограничение отключается.

Для PostgreSQL этот параметр обычно не нужен.

## 7. `DeclarativeBase` и `Base`

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

`Base` — общий базовый класс для ORM-моделей.

Модель таблицы наследуется от него:

```python
class Application(Base):
    ...
```

SQLAlchemy регистрирует такую модель в:

```python
Base.metadata
```

`metadata` содержит описание таблиц, колонок, типов и ограничений. Самих заявок там нет.

## 8. Модель SQLAlchemy — Python-класс, связанный с таблицей базы

В `app/db/models.py`:

```python
class Application(Base):
    __tablename__ = "applications"
```

`__tablename__` задаёт имя таблицы. `Base` связывает этот класс с SQLAlchemy ORM.

### Колонка `id`: `Mapped` — тип Python, `mapped_column` — описание колонки

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

`Mapped[int]` означает, что в Python поле является целым числом. `mapped_column(...)` описывает, как поле хранится в базе. `primary_key=True` делает `id` первичным ключом, который идентифицирует заявку.

### Строковые колонки: `String` — ограниченная строка

```python
company: Mapped[str] = mapped_column(String(255))
position: Mapped[str] = mapped_column(String(255))
url: Mapped[str] = mapped_column(String(2048))
```

`Mapped[str]` сообщает Python-тип, `mapped_column` связывает атрибут с колонкой, а `String(255)` ограничивает строку длиной до 255 символов. Для URL используется `String(2048)`.

### Длинный текст: `Text` — строка без короткого ограничения длины

```python
description: Mapped[str] = mapped_column(Text)
```

`Text` используется для описаний, длина которых заранее неизвестна. В отличие от `String(255)`, здесь не задаётся короткий лимит длины.

### Значения по умолчанию

```python
status: Mapped[str] = mapped_column(
    String(50),
    default="new",
)
```

Если статус не передан, ORM использует `new`.

```python
source: Mapped[str] = mapped_column(
    String(50),
    default="telegram",
)
```

Источник по умолчанию — `telegram`.

### Даты: `DateTime` — дата и время, `func.now()` — текущее время базы

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
)
```

`DateTime(timezone=True)` хранит дату и время с поддержкой часового пояса. `server_default=func.now()` означает, что текущее время устанавливает сама база данных при создании записи.

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
)
```

`onupdate=func.now()` задаёт обновление времени при изменении записи. `func.now()` — SQLAlchemy-представление SQL-функции текущего времени.

## 9. `Base.metadata.create_all`

В `database.py`:

```python
def init_db() -> None:
    from app.db.models import Application

    Base.metadata.create_all(bind=engine)
```

Что происходит:

1. импортируется модель `Application`;
2. модель регистрируется в `Base.metadata`;
3. SQLAlchemy проверяет существующие таблицы;
4. отсутствующая таблица `applications` создаётся.

`create_all` не удаляет существующие данные. Но это не полноценные миграции: изменение существующей таблицы нужно делать через Alembic или отдельный SQL.

## 10. `sessionmaker`

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
```

`SessionLocal` — фабрика объектов `Session`.

Каждый вызов:

```python
db = SessionLocal()
```

создаёт новую сессию.

Параметры:

- `bind=engine` — работать через созданный engine;
- `autocommit=False` — сохранять изменения только после `commit()`;
- `autoflush=False` — не отправлять изменения автоматически перед каждым запросом.

## 11. `Session`

`Session` — временный рабочий контекст для операций с базой.

Она умеет:

- выполнять SELECT;
- добавлять объекты;
- изменять объекты;
- удалять объекты;
- подтверждать транзакции;
- откатывать транзакции.

Сессия не является самой базой и не хранит данные после закрытия. Данные сохраняются благодаря `commit()`.

## 12. `get_db`

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Порядок:

1. создаётся Session;
2. Session передаётся endpoint-у;
3. endpoint выполняет операции;
4. Session закрывается.

В FastAPI она подключается через dependency:

```python
db: Session = Depends(get_db)
```

## 13. `add` — добавить объект в текущую сессию

```python
application = Application(**payload.model_dump())
db.add(application)
```

Объект подготовлен к сохранению, но транзакция ещё не подтверждена.

## 14. `commit` — подтвердить транзакцию и сохранить изменения

```python
db.commit()
```

Изменения записываются в `app.db` только после подтверждения транзакции.

Создание заявки:

```python
db.add(application)
db.commit()
```

Если вызвать только `add`, а затем закрыть сессию без `commit`, запись не должна считаться сохранённой.

## 15. `refresh` — перечитать объект из базы

```python
db.refresh(application)
```

После сохранения объект повторно загружается из базы.

Это нужно после создания, чтобы получить значения, сгенерированные базой:

- `id`;
- `created_at`;
- `updated_at`.

Полная последовательность:

```python
db.add(application)
db.commit()
db.refresh(application)
```

## 16. `get` — найти объект по первичному ключу

```python
application = db.get(Application, application_id)
```

Поиск выполняется по первичному ключу `id`.

Пример:

```python
application = db.get(Application, 1)
```

Это соответствует смыслу запроса:

```sql
SELECT * FROM applications WHERE id = 1;
```

Если запись не найдена, результатом будет `None`.

## 17. `select` — построить запрос на чтение

```python
from sqlalchemy import select

statement = select(Application).order_by(Application.id)
applications = db.scalars(statement).all()
```

Запрос формируется, но сам по себе ещё не возвращает результаты.

`order_by(Application.id)` сортирует результат по идентификатору.

`db.scalars(statement)` выполняет запрос и извлекает ORM-объекты из результата.

`all()` получает все результаты в виде списка Python.

## 18. Изменение объекта

В `applications.py`:

```python
for field, value in payload.model_dump(exclude_unset=True).items():
    if value is not None:
        setattr(application, field, value)
```

`setattr` изменяет поле ORM-объекта.

После изменения нужно выполнить:

```python
db.commit()
db.refresh(application)
```

Пример PATCH:

```json
{
  "status": "interview"
}
```

Изменяется только статус.

## 19. Транзакции и `rollback`

Транзакция — группа изменений, которая подтверждается целиком.

Если произошла ошибка, изменения можно отменить:

```python
try:
    db.add(application)
    db.commit()
except Exception:
    db.rollback()
    raise
```

`rollback()` возвращает базу к состоянию до незавершённой транзакции.

`close()` закрывает сессию, но сам по себе не заменяет `commit()` или `rollback()`.

## 20. Связь SQLAlchemy с API

```text
FastAPI endpoint
    -> Depends(get_db)
    -> Session
    -> Application model
    -> SQLAlchemy operation
    -> SQLite app.db
```

Создание заявки:

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

Получение заявок:

```python
@router.get("")
def list_applications(db: Session = Depends(get_db)):
    statement = select(Application).order_by(Application.id)
    return {"applications": db.scalars(statement).all()}
```

## 21. Порядок работы при добавлении новой таблицы

1. Добавить библиотеку или драйвер в `requirements.txt`.
2. Добавить URL базы в `config.py` или `.env`.
3. Использовать общий `Base` из `database.py`.
4. Создать новую модель в `models.py`.
5. Убедиться, что модель импортируется до `create_all`.
6. Создать схемы Pydantic для входных и выходных данных.
7. Добавить endpoint в роутер.
8. Получить `Session` через `Depends(get_db)`.
9. Реализовать `select`, `add`, `commit`, `get` или другие операции.
10. Проверить API через Swagger.

## 22. SQLAlchemy и миграции

`create_all` подходит для первого создания таблиц. Если таблица уже существует и нужно добавить колонку, лучше использовать Alembic.

Пример изменения модели:

```python
salary: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

Само изменение Python-класса не изменит автоматически уже существующую таблицу во всех окружениях. Для контролируемого изменения структуры используют миграции.

## 23. Итоговая схема

```text
config.py
    database_url
        ↓
database.py
    engine, Base, SessionLocal, get_db
        ↓
models.py
    Application и колонки таблицы
        ↓
applications.py
    select, add, get, commit, refresh
        ↓
app.db
    сохранённые заявки
```
