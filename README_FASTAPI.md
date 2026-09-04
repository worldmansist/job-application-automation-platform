# FastAPI в проекте

## 1. Что такое FastAPI

FastAPI — Python-фреймворк для создания веб-API. Он принимает HTTP-запросы, проверяет входные данные, вызывает нужную функцию и возвращает ответ клиенту.

В проекте FastAPI используется как backend для работы с заявками на вакансии.

Общий путь запроса:

```text
Клиент или Swagger
    -> HTTP-запрос
    -> FastAPI
    -> роутер
    -> функция endpoint
    -> SQLAlchemy и база данных
    -> HTTP-ответ
```

## 2. Запуск приложения

Из корня проекта:

```powershell
cd C:\Users\user\Documents\Project
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Документация Swagger:

```text
http://127.0.0.1:8000/docs
```

Документация ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## 3. Главный объект `FastAPI`

В `app/main.py` создаётся приложение:

```python
from fastapi import FastAPI

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Job Application Automation Platform",
)
```

`app` — главный объект приложения. Через него подключаются маршруты и события запуска.
`settings` — объект настроек из `app/core/config.py`; `settings.app_name` подставляет название приложения из конфигурации.

Параметры:

- `title` — название API в Swagger;
- `version` — версия API;
- `description` — описание проекта.

## 4. Endpoint

Endpoint — функция, связанная с HTTP-методом и URL.

Пример в `app/main.py`:

```python
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
    }
```

Здесь:

- `@app.get("/")` означает GET-запрос по адресу `/`;
- `root` — функция, которая будет вызвана;
- возвращаемый словарь автоматически превращается в JSON.

## 5. HTTP-методы

В API заявок используются:

```text
GET   /applications              получить все заявки
GET   /applications/{id}         получить одну заявку
POST  /applications              создать заявку
PATCH /applications/{id}         изменить заявку
```

### GET

GET используется для чтения данных:

```python
@router.get("")
def list_applications(db: Session = Depends(get_db)):
    ...
```

### POST

POST используется для создания данных:

```python
@router.post("")
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
):
    ...
```

`payload` содержит JSON, отправленный клиентом.
Это объект схемы `ApplicationCreate`, уже проверенный Pydantic.

### PATCH

PATCH используется для частичного изменения существующей записи:

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

Для группировки связанных endpoint-ов используется роутер:

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)
```
`prefix` задаёт общий URL `/applications`, а `tags` объединяет эти endpoint-ы в одну группу Swagger с названием `applications`.

`prefix` — общий префикс, который добавляется к каждому маршруту.

Поэтому:

```python
@router.get("")
```

становится:

```text
GET /applications
```

А:

```python
@router.get("/{application_id}")
```

становится:

```text
GET /applications/{application_id}
```

Роутер подключается в `main.py`:

```python
app.include_router(applications_router)
```

## 7. Pydantic-схемы и проверка данных

В `app/schemas/application.py` описаны входные данные:

```python
class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    status: str = "new"
    source: str = "telegram"
```

FastAPI автоматически проверяет JSON до запуска endpoint-а.

Пример корректного запроса:

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

Если обязательное поле отсутствует или пустое, FastAPI возвращает ошибку `422 Unprocessable Entity`.

## 8. Создание заявки через API

Функция:

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

Здесь `db.add()` добавляет объект в текущую сессию, `db.commit()` подтверждает транзакцию и сохраняет запись, а `db.refresh()` перечитывает запись из базы, чтобы получить созданные `id` и даты.

Порядок работы:

1. FastAPI получает JSON;
2. Pydantic проверяет данные;
3. `payload.model_dump()` превращает схему в словарь;
4. создаётся модель SQLAlchemy;
5. запись добавляется в базу;
6. API возвращает JSON-ответ.

## 9. Dependency Injection и `Depends`

В endpoint-е написано:

```python
db: Session = Depends(get_db)
```

`Depends` говорит FastAPI: перед вызовом функции получи значение через `get_db`.

`get_db` создаёт сессию базы:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI автоматически передаёт `db` в endpoint и после запроса позволяет закрыть сессию.

## 10. Path-параметры

В маршруте:

```python
@router.get("/{application_id}")
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    ...
```

`application_id` берётся из URL:

```text
GET /applications/5
```

Значение `5` автоматически преобразуется в `int`. Если передать строку вместо числа, FastAPI вернёт ошибку валидации.

## 11. Ошибки API

Если заявка не найдена:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail="Application not found",
)
```

Клиент получает JSON:

```json
{
  "detail": "Application not found"
}
```

Частые статусы:

- `200` — успешное чтение или изменение;
- `201` — ресурс создан, если endpoint настроен на такой статус;
- `404` — запись не найдена;
- `422` — входные данные не прошли проверку;
- `500` — внутренняя ошибка сервера.

## 12. Событие запуска

В `main.py` приложение вызывает инициализацию базы при запуске:

```python
@app.on_event("startup")
def startup() -> None:
    init_db()
```

До обработки запросов FastAPI вызывает `init_db`, после чего таблица `applications` готова к работе.

## 13. Swagger

Swagger создаётся FastAPI автоматически.

Для создания заявки:

1. открыть `/docs`;
2. найти `POST /applications`;
3. нажать `Try it out`;
4. вставить JSON;
5. нажать `Execute`.

Для просмотра заявок использовать `GET /applications`.

## 14. Связь FastAPI с остальным кодом

```text
app/main.py
    создаёт FastAPI и подключает роутеры
        ↓
app/api/routes/applications.py
    принимает HTTP-запросы
        ↓
app/schemas/application.py
    проверяет входные данные
        ↓
app/db/database.py
    выдаёт Session
        ↓
app/db/models.py
    описывает таблицу Application
        ↓
app.db
    хранит данные
```

## 15. Словарь терминов

### API

API — интерфейс, через который одна программа взаимодействует с другой. В нашем случае клиент отправляет HTTP-запросы FastAPI.

Пример:

```text
POST /applications
```

### FastAPI

FastAPI — Python-фреймворк, который принимает HTTP-запросы, вызывает нужные функции и формирует ответы.

### Endpoint

Endpoint — конкретная функция API, связанная с HTTP-методом и адресом.

```python
@router.get("")
def list_applications():
    ...
```

Эта функция обслуживает запрос `GET /applications`.

### Router и `APIRouter`

Router — группа связанных маршрутов. `APIRouter` создаёт такой объект:

```python
router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)
```

### `prefix`

`prefix` — общий начальный фрагмент URL для всех маршрутов роутера.

```python
prefix="/applications"
```

Поэтому маршрут:

```python
@router.get("")
```

получает полный адрес:

```text
GET /applications
```

А `@router.get("/{application_id}")` становится `GET /applications/{application_id}`.

### `tags`

`tags` — название группы endpoint-ов в Swagger.

```python
tags=["applications"]
```

Это не таблица базы и не URL. Тег нужен для удобной группировки маршрутов в документации.

### Swagger / OpenAPI

Swagger UI — веб-страница для просмотра и проверки API. В FastAPI она доступна по адресу `/docs`.

OpenAPI — стандартное описание API: маршрутов, параметров, схем запросов и ответов. FastAPI автоматически создаёт его на основе Python-кода и Pydantic-моделей.

Swagger позволяет нажать `Try it out`, заполнить JSON и отправить настоящий запрос к приложению.

### ReDoc

ReDoc — альтернативный интерфейс документации OpenAPI. В проекте он доступен по адресу `/redoc`.

Swagger удобнее для ручного тестирования, а ReDoc часто удобнее для чтения документации.

### Pydantic

Pydantic — библиотека проверки и преобразования данных.

В проекте она используется в файле `app/schemas/application.py`:

```python
class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1)
```

Pydantic проверяет, что:

- поле `company` существует;
- значение является строкой;
- строка содержит хотя бы один символ.

Если данные неправильные, FastAPI не запускает endpoint и возвращает ошибку `422`.

### `BaseModel`

`BaseModel` — базовый класс Pydantic. От него наследуются схемы входных и выходных данных.

```python
class ApplicationCreate(BaseModel):
    ...
```

### Schema / схема

Схема — описание формы данных, которые API принимает или возвращает.

Например, `ApplicationCreate` описывает данные для создания заявки, а `ApplicationUpdate` — поля, которые можно изменить.

Схема Pydantic и модель SQLAlchemy — разные вещи:

```text
Pydantic-схема  → проверяет HTTP-данные
SQLAlchemy-модель → описывает таблицу базы
```

### `payload`

`payload` — переменная с данными тела HTTP-запроса.

```python
def create_application(payload: ApplicationCreate):
    ...
```

Если клиент отправил JSON:

```json
{
  "company": "Google",
  "position": "Python Developer"
}
```

FastAPI проверяет его и передаёт функции как объект `payload` типа `ApplicationCreate`.

### Request body / тело запроса

Тело запроса — данные, отправленные клиентом внутри HTTP-запроса. Для `POST /applications` это JSON с информацией о вакансии.

### Path parameter / параметр пути

Параметр пути находится прямо в URL:

```python
@router.get("/{application_id}")
```

Запрос:

```text
GET /applications/5
```

передаст функции значение `application_id = 5`.

### `settings`

`settings` — объект с настройками приложения из `app/core/config.py`.

```python
from app.core.config import settings

app_name = settings.app_name
```

В настройках проекта хранятся:

```python
app_name
environment
database_url
telegram_bot_token
api_base_url
```

Значения могут быть заданы по умолчанию или прочитаны из `.env`.

### `.env`

`.env` — файл переменных окружения. В нём удобно хранить настройки, которые не должны быть жёстко записаны в коде.

Пример:

```env
DATABASE_URL=sqlite:///./app.db
TELEGRAM_BOT_TOKEN=your_token_here
```

Секретные токены не следует добавлять в Git.

### `Depends`

`Depends` — механизм Dependency Injection в FastAPI.

```python
db: Session = Depends(get_db)
```

Это означает: перед запуском endpoint вызови `get_db` и передай результат в параметр `db`.

В нашем случае FastAPI автоматически:

1. создаёт Session;
2. передаёт её функции;
3. после запроса закрывает Session.

### Dependency Injection

Dependency Injection — передача готовой зависимости функции извне.

Endpoint не создаёт сессию вручную:

```python
def list_applications(db: Session = Depends(get_db)):
    ...
```

FastAPI сам управляет получением `db` через `get_db`.

### `Session`

`Session` — временный рабочий объект SQLAlchemy для чтения и изменения данных в базе.

```python
db: Session
```

Session не является самой базой и не хранит данные после закрытия. Данные сохраняются через `commit()`.

### `db.add()`

`add()` добавляет объект в текущую сессию:

```python
db.add(application)
```

На этом шаге объект подготовлен к сохранению, но транзакция ещё не подтверждена.

### `db.commit()`

`commit()` подтверждает транзакцию и сохраняет изменения в `app.db`:

```python
db.commit()
```

Без `commit()` новая заявка может не сохраниться после закрытия Session.

### `db.refresh()`

`refresh()` заново загружает объект из базы:

```python
db.refresh(application)
```

После создания это позволяет получить значения, которые назначила база:

- `id`;
- `created_at`;
- `updated_at`.

### `db.get()`

`get()` ищет запись по первичному ключу:

```python
application = db.get(Application, application_id)
```

Если запись не существует, результатом будет `None`.

### `select()`

`select()` создаёт SQLAlchemy-запрос на чтение:

```python
statement = select(Application).order_by(Application.id)
applications = db.scalars(statement).all()
```

`order_by` задаёт сортировку, `scalars` извлекает ORM-объекты, а `all` получает все результаты.

### `model_dump()`

`model_dump()` превращает Pydantic-объект в обычный Python-словарь:

```python
data = payload.model_dump()
application = Application(**data)
```

Оператор `**` передаёт элементы словаря как именованные аргументы конструктора.

### `exclude_unset=True`

Этот параметр оставляет только поля, которые клиент действительно передал:

```python
payload.model_dump(exclude_unset=True)
```

Это важно для `PATCH`: если клиент меняет только `status`, остальные поля не затираются.

### `HTTPException`

`HTTPException` останавливает обработку и возвращает клиенту HTTP-ошибку:

```python
raise HTTPException(
    status_code=404,
    detail="Application not found",
)
```

### `status_code`

`status_code` — числовой результат HTTP-запроса.

Основные значения в проекте:

- `200` — операция выполнена;
- `404` — заявка не найдена;
- `422` — данные не прошли проверку;
- `500` — ошибка сервера.

### JSON

JSON — текстовый формат обмена данными между клиентом и API.

Python-словарь:

```python
{"company": "Google"}
```

передаётся клиенту как JSON:

```json
{"company": "Google"}
```

### ORM

ORM расшифровывается как Object-Relational Mapping — объектно-реляционное отображение.

Вместо ручного SQL мы работаем с объектом:

```python
application = Application(...)
```

SQLAlchemy связывает его с таблицей `applications`.

### `startup`

`startup` — событие запуска FastAPI:

```python
@app.on_event("startup")
def startup() -> None:
    init_db()
```

Перед обработкой запросов вызывается `init_db`, который создаёт отсутствующие таблицы.

### `uvicorn`

Uvicorn — ASGI-сервер, который запускает FastAPI-приложение:

```powershell
python -m uvicorn app.main:app --reload
```

В записи `app.main:app`:

- `app.main` — Python-модуль `app/main.py`;
- `app` — объект FastAPI внутри этого модуля.

Флаг `--reload` перезапускает сервер после изменения кода и используется в разработке.

FastAPI отвечает за HTTP-слой. Он не является базой данных и не хранит заявки самостоятельно.
