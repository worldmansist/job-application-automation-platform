# Руководство по запуску проекта

## Предварительные требования

- Python 3.8 или выше
- pip (обычно поставляется с Python)

## Шаг 1: Создание и активация виртуального окружения

### На Windows:

Если виртуальное окружение еще не создано, выполните в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если окружение уже создано, выполните только команду активации:

```powershell
.\.venv\Scripts\Activate.ps1
```

Если получаете ошибку политики выполнения (`ExecutionPolicy`), используйте:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Или используйте Command Prompt вместо PowerShell.

### На macOS/Linux:

```bash
source .venv/bin/activate
```

Если виртуальное окружение еще не создано, создайте его:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Шаг 2: Установка зависимостей

После активации виртуального окружения выполните:

```bash
pip install -r requirements.txt
```

## Шаг 3: Настройка переменных окружения

Создайте файл `.env` в корне проекта и добавьте токен Telegram:

```env
TELEGRAM_BOT_TOKEN=your_token_here
API_BASE_URL=http://127.0.0.1:8000
```

## Шаг 4: Запуск приложения и бота

В проекте нужно запускать два процесса в разных терминалах.

### Терминал 1: FastAPI

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: **http://localhost:8000**

### Терминал 2: Telegram Bot

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.bot.main
```

### Опции запуска:

- `--reload` — автоматическая перезагрузка при изменении файлов (для разработки)
- `--host 0.0.0.0` — доступно из других компьютеров в сети
- `--port 8080` — использовать другой порт вместо 8000

Пример запуска API на другом порту:

```powershell
uvicorn app.main:app --reload --port 8080
```

## Документация API

После запуска приложения вы можете просмотреть документацию API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Деактивация виртуального окружения

Когда закончите работу, деактивируйте окружение:

```bash
deactivate
```

## Полная последовательность команд для быстрого старта

### Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Создайте файл `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token_here
API_BASE_URL=http://127.0.0.1:8000
```

Запуск в двух терминалах:

```powershell
# Терминал 1
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

```powershell
# Терминал 2
.\.venv\Scripts\Activate.ps1
python -m app.bot.main
```

### macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
# Терминал 1
uvicorn app.main:app --reload
```

```bash
# Терминал 2
python -m app.bot.main
```
