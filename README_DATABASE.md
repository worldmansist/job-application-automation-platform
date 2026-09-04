# Как работает подключение базы данных

Этот файл объясняет подключение SQLite и SQLAlchemy в проекте простыми шагами.

## 1. Что было до подключения базы

Изначально заявки хранились в обычном списке Python:

```python
applications = []
```

При создании заявки объект добавлялся в этот список. Проблема в том, что список существует только пока работает процесс Python. После перезапуска FastAPI все заявки исчезали.

Теперь данные проходят такой путь:

```text
HTTP-запрос
    -> FastAPI
    -> SQLAlchemy Session
    -> модель Application
    -> таблица applications
    -> файл app.db
```

Файл `app.db` является локальной SQLite-базой проекта.

## 2. Какие библиотеки участвуют

### FastAPI

FastAPI принимает HTTP-запросы и вызывает функции из `app/api/routes/applications.py`.

В проекте используются маршруты:

```text
GET   /applications
GET   /applications/{application_id}
POST  /applications
PATCH /applications/{application_id}
```

FastAPI также проверяет входные данные через Pydantic-схемы из `app/schemas/application.py`.

### SQLAlchemy

SQLAlchemy связывает Python-классы с таблицами базы данных.

Вместо ручного SQL мы работаем с объектами Python:

```python
application = Application(**payload.model_dump())
db.add(application)
db.commit()
```

SQLAlchemy превращает эти операции в SQL-запросы к SQLite.

### SQLite

SQLite является самой базой данных. В нашем случае она хранится в одном файле:

```text
app.db
```

Для начала разработки это удобно: не нужно устанавливать отдельный сервер PostgreSQL.

### Pydantic Settings

`pydantic-settings` читает настройки приложения из переменных окружения и файла `.env`.

Благодаря этому адрес базы не нужно жёстко прописывать в каждом файле.

## 3. Порядок внесения изменений

Изменения должны вноситься снизу вверх по цепочке зависимостей:

```text
1. requirements.txt  - установить библиотеку
2. config.py         - добавить адрес базы
3. database.py       - создать engine и Session
4. models.py         - описать таблицы
5. main.py           - создать таблицы при запуске
6. applications.py   - использовать БД в API
7. Проверка          - создать и прочитать заявку
```

Такой порядок важен: роутер не может импортировать модель, если модель ещё не создана, а модель не может подключиться без `engine` и настроек.

## 4. Файл `requirements.txt`

Добавлена строка:

```text
sqlalchemy==2.0.36
```

Она устанавливает SQLAlchemy фиксированной версии.

После изменения зависимостей выполняется:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Использование Python из `.venv` гарантирует, что библиотека установится именно в окружение проекта.

## 5. Файл `app/core/config.py`

Добавлена настройка:

```python
database_url: str = "sqlite:///./app.db"
```

Это адрес базы данных.

Разбор значения:

- `sqlite` — используемый тип базы;
- `./app.db` — файл в текущей рабочей папке проекта;
- `database_url` — имя настройки Python;
- `DATABASE_URL` — соответствующее имя переменной в `.env`.

Можно создать `.env` в корне проекта:

```env
DATABASE_URL=sqlite:///./app.db
```

Если переменная не указана, используется значение по умолчанию из `config.py`.

Позже SQLite можно заменить на PostgreSQL, изменив только адрес и установив драйвер PostgreSQL. Роутеры при этом останутся почти такими же.

## 6. Файл `app/db/database.py`

Этот файл является общей точкой подключения к базе.

### `Base`

```python
class Base(DeclarativeBase):
    pass
```

`Base` — общий родитель моделей SQLAlchemy. Все модели, унаследованные от него, попадают в метаданные:

```python
Base.metadata
```

По этим метаданным SQLAlchemy понимает, какие таблицы нужно создать.

### `connect_args`

```python
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
```

SQLite имеет ограничение на использование соединений из разных потоков. FastAPI может обрабатывать запросы в разных потоках, поэтому для SQLite передаётся `check_same_thread=False`.

Для PostgreSQL эта настройка не нужна, поэтому передаётся пустой словарь.

### `engine`

```python
engine = create_engine(
    settings.database_url,
    connect_args=connect_args
)
```

`engine` знает, где находится база и как к ней подключаться. Он не является одной конкретной заявкой или одной сессией.

### `SessionLocal`

```python
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
```

`sessionmaker` — фабрика сессий. Каждый вызов создаёт отдельный рабочий объект:

```python
db = SessionLocal()
```

Параметры:

- `bind=engine` — сессия работает через наш `engine`;
- `autocommit=False` — изменения нужно подтверждать через `db.commit()`;
- `autoflush=False` — SQLAlchemy не отправляет накопленные изменения автоматически перед каждым запросом.

### `get_db`

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Функция создаёт сессию, передаёт её обработчику FastAPI и закрывает после завершения запроса.

`yield` нужен, чтобы FastAPI временно получил объект `db`.

Сессия не равна базе данных. Это временный рабочий контекст для операций с базой.

### `init_db`

```python
def init_db() -> None:
    from app.db.models import Application

    Base.metadata.create_all(bind=engine)
```

`create_all` создаёт таблицы, которых ещё нет.

Импорт `Application` внутри функции нужен, чтобы модель была зарегистрирована в `Base.metadata` до вызова `create_all`.

## 7. Файл `app/db/models.py`

Модель описывает таблицу базы:

```python
class Application(Base):
    __tablename__ = "applications"
```

Это означает: класс `Application` связан с таблицей `applications`.

### Поля модели

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

Первичный ключ заявки. SQLite автоматически выдаёт новые значения `id`.

```python
company: Mapped[str] = mapped_column(String(255))
position: Mapped[str] = mapped_column(String(255))
url: Mapped[str] = mapped_column(String(2048))
```

Текстовые поля компании, должности и ссылки.

```python
description: Mapped[str] = mapped_column(Text)
```

Длинное описание вакансии.

```python
status: Mapped[str] = mapped_column(String(50), default="new")
source: Mapped[str] = mapped_column(String(50), default="telegram")
```

Статус и источник заявки. Если значения не переданы, используются значения по умолчанию.

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
)
```

Дата создания устанавливается базой.

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now()
)
```

Дата создания устанавливается при добавлении, а `onupdate` просит SQLAlchemy обновлять её при изменении записи.

Итоговая таблица:

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

## 8. Файл `app/main.py`

В главный файл добавлен импорт:

```python
from app.db.database import init_db
```

И обработчик запуска:

```python
@app.on_event("startup")
def startup() -> None:
    init_db()
```

Когда запускается FastAPI, вызывается `startup`, а затем `init_db`.

Если файла `app.db` ещё нет, SQLite создаёт его. Затем SQLAlchemy создаёт таблицу `applications`.

Это происходит автоматически при запуске:

```powershell
python -m uvicorn app.main:app --reload
```

Важно: `create_all` создаёт отсутствующие таблицы, но не является полноценной системой миграций. Если существующую таблицу нужно изменить, позже понадобится Alembic.

## 9. Файл `app/api/routes/applications.py`

Здесь API переключён со списка Python на базу.

### Подключение зависимостей

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Application
```

- `Depends` просит FastAPI передать сессию;
- `Session` используется для аннотации типа;
- `select` создаёт запрос на выборку;
- `Application` представляет таблицу;
- `get_db` создаёт и закрывает сессию.

### Получение всех заявок

```python
def list_applications(db: Session = Depends(get_db)):
    return {
        "applications": db.scalars(
            select(Application).order_by(Application.id)
        ).all()
    }
```

FastAPI вызывает `get_db`, получает `db`, затем выполняется запрос к таблице.

`scalars` извлекает объекты `Application`, а `all` превращает результат в список.

### Получение одной заявки

```python
application = db.get(Application, application_id)
```

Поиск выполняется по первичному ключу `id`.

Если записи нет, API возвращает:

```python
raise HTTPException(status_code=404, detail="Application not found")
```

### Создание заявки

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

Порядок действий:

1. `ApplicationCreate` проверяет входной JSON;
2. `model_dump()` превращает Pydantic-объект в словарь;
3. `Application(...)` создаёт объект модели SQLAlchemy;
4. `db.add()` добавляет его в текущую транзакцию;
5. `db.commit()` сохраняет его в SQLite;
6. `db.refresh()` загружает сгенерированные `id` и даты.

### Изменение заявки

```python
for field, value in payload.model_dump(exclude_unset=True).items():
    if value is not None:
        setattr(application, field, value)
```

`exclude_unset=True` позволяет изменить только поля, которые пришли в запросе.

Например:

```json
{
  "status": "interview"
}
```

изменит только статус, а остальные поля останутся прежними.

После изменения выполняется:

```python
db.commit()
db.refresh(application)
```

## 10. Полный сценарий создания заявки

```text
1. Клиент отправляет POST /applications
2. FastAPI получает JSON
3. ApplicationCreate проверяет данные
4. Depends(get_db) создаёт Session
5. Создаётся объект Application
6. db.add() добавляет его в транзакцию
7. db.commit() записывает его в app.db
8. db.refresh() получает id и даты
9. API возвращает заявку
10. get_db закрывает Session
```

После перезапуска сервера запись остаётся, потому что она находится в `app.db`, а не в оперативной памяти Python.

## 11. Как проверить работу

Запустить приложение из корня проекта:

```powershell
cd C:\Users\user\Documents\Project
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Открыть Swagger:

```text
http://127.0.0.1:8000/docs
```

Через `POST /applications` создать заявку:

```json
{
  "company": "Google",
  "position": "Python Developer",
  "url": "https://example.com/vacancy",
  "description": "Backend-разработка на Python",
  "status": "new",
  "source": "manual"
}
```

Затем выполнить `GET /applications` и проверить, что заявка появилась.

После этого остановить сервер через `Ctrl+C`, запустить снова и повторить `GET /applications`. Запись должна сохраниться.

## 12. Важное различие между компонентами

```text
config.py       знает адрес базы
    ↓
database.py     создаёт engine и Session
    ↓
models.py       описывает таблицы
    ↓
main.py         запускает создание таблиц
    ↓
applications.py выполняет операции API
```

- `engine` знает, как подключаться к базе;
- `Session` выполняет конкретные операции;
- `Application` описывает структуру таблицы;
- `db.add`, `db.commit`, `db.get` работают через сессию;
- FastAPI связывает HTTP-запрос с функцией роутера.

## 13. Что делать дальше

Текущая версия подходит для первого локального этапа. Следующие шаги:

1. Добавить обработку `rollback()` при ошибках.
2. Создать тесты для всех endpoint-ов.
3. Подключить Alembic для миграций.
4. Добавить таблицы компаний, статусов и истории изменений.
5. Переключить SQLite на PostgreSQL, когда появится необходимость в общей серверной базе.
