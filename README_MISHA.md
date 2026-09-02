# Этап 0: настройка и запуск проекта

## Что сделано на этапе 0

- настроено виртуальное окружение Python;
- установлены зависимости;
- добавлены FastAPI backend и Telegram-бот;
- настроены переменные окружения;
- проверен запуск API и бота.

## Создание среды

Выполнять из корневой папки проекта в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если PowerShell блокирует активацию:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

После активации в начале строки терминала появится `(.venv)`.

## Установка зависимостей

```powershell
pip install -r requirements.txt
```

## Настройка `.env`

Создай файл `.env` в корне проекта:

```env
APP_NAME="Job Application Automation Platform"
ENVIRONMENT="development"
TELEGRAM_BOT_TOKEN="токен_от_BotFather"
```

Файл `.env` нельзя добавлять в GitHub.

## Запуск FastAPI

В первом терминале:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

API и документация:

- http://localhost:8000
- http://localhost:8000/docs

## Запуск Telegram-бота

Во втором терминале:

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.bot.main
```

После запуска отправь боту в Telegram команду `/start`.

Не запускай два экземпляра одного бота одновременно: Telegram выдаст ошибку `Conflict`.

## Проверка проекта

```powershell
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -c "import app.bot.main; print('BOT_MODULE_OK')"
```