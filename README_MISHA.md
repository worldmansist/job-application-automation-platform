# Настройка Python-окружения в проекте

## 1. Создание папки проекта

В PowerShell открыл терминал и создал папку проекта:

```powershell
mkdir Project
```

Затем перешёл в эту папку:

```powershell
cd Project
```

## 2. Создание файлов проекта

Создал файл README:

```powershell
New-Item README.md
```

Также создал основной файл проекта, например:

```powershell
New-Item app.py
```

Если нужен был ещё один файл, например для зависимостей, то создавал так:

```powershell
New-Item requirements.txt
```

После этого открыл папку проекта в VS Code и начал настройку Python.

## 3. Выбор интерпретатора

Сначала я открыл VS Code и выбрал интерпретатор через горячие клавиши:

- `Ctrl + Shift + P`
- `Python: Select Interpreter`

После этого окружение не появилось автоматически, поэтому я создал его вручную.

## 4. Создание виртуального окружения

В корне проекта выполнил команду:

```powershell
python -m venv .venv
```

Эта команда создала папку `.venv` с локальной средой Python.

## 5. Разблокировка запуска сценариев в PowerShell

Так как PowerShell блокировал запуск скриптов, я выполнил:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Это разрешило запуск активационного скрипта только для текущей сессии терминала.

## 6. Активация окружения

После этого активировал среду командой:

```powershell
.\.venv\Scripts\Activate.ps1
```

После активации в терминале появилось подтверждение вида:

```powershell
(.venv)
```

Это означает, что виртуальная среда успешно активирована.

## 7. Проверка работы Python

Проверил, что Python работает из активированного окружения:

```powershell
python --version
```

При необходимости можно обновить `pip`:

```powershell
python -m pip install --upgrade pip
```

## Итог

Теперь проект работает в изолированной Python-среде, и все зависимости можно устанавливать локально без влияния на глобальную систему.

## Этап 0: что уже сделано в проекте

После настройки окружения мы начали первый рабочий этап проекта.

### 1. Создан базовый каркас приложения

Сформировали структуру проекта:

```text
Project/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   ├── core/
│   │   └── config.py
│   └── main.py
├── .env.example
├── requirements.txt
├── README_MISHA.md
└── PLAN_PROEKT.md
```

### 2. Настроен FastAPI

Создали базовое приложение в файле:

```python
from fastapi import FastAPI

app = FastAPI(title="Job Application Automation Platform")
```

### 3. Добавлен health-check endpoint

В маршруте `/health` добавили проверку статуса сервиса:

```python
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "job-app-platform",
    }
```

### 4. Добавлены настройки проекта

Создали файл конфигурации с переменными окружения:

```python
class Settings(BaseSettings):
    app_name: str = "Job Application Automation Platform"
    environment: str = "development"
```

### 5. Установлены зависимости

В `requirements.txt` добавлены минимальные пакеты:

```text
fastapi==0.115.0
uvicorn[standard]==0.30.1
pydantic-settings==2.3.4
```

### 6. Проверка запуска

Запустили приложение командой:

```powershell
python -m uvicorn app.main:app --reload
```

Сервер успешно запустился и показал:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Это означает, что этап 0 закрыт: базовый проект запущен и готов к дальнейшему развитию.
