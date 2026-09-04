# Project Startup Guide

## Prerequisites

- Python 3.8 or later
- pip (usually included with Python)

## Step 1: Create and Activate a Virtual Environment

### On Windows:

If the virtual environment has not been created yet, run this in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If the environment already exists, run only the activation command:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you receive an execution policy error (`ExecutionPolicy`), use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Or use Command Prompt instead of PowerShell.

### On macOS/Linux:

```bash
source .venv/bin/activate
```

If the virtual environment has not been created yet, create it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Step 2: Install Dependencies

After activating the virtual environment, run:

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

Create an `.env` file in the project root and add the Telegram token:

```env
TELEGRAM_BOT_TOKEN=your_token_here
API_BASE_URL=http://127.0.0.1:8000
```

## Step 4: Start the Application and Bot

The project requires two processes running in separate terminals.

### Terminal 1: FastAPI

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

The application will be available at: **http://localhost:8000**

### Terminal 2: Telegram Bot

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.bot.main
```

### Startup Options:

- `--reload` — automatically reload when files change (for development)
- `--host 0.0.0.0` — available from other computers on the network
- `--port 8080` — use a different port instead of 8000

Example of starting the API on another port:

```powershell
uvicorn app.main:app --reload --port 8080
```

## API Documentation

After starting the application, you can view the API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Deactivate the Virtual Environment

When you finish, deactivate the environment:

```bash
deactivate
```

## Complete Quick-Start Command Sequence

### Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create an `.env` file:

```env
TELEGRAM_BOT_TOKEN=your_token_here
API_BASE_URL=http://127.0.0.1:8000
```

Start in two terminals:

```powershell
# Terminal 1
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

```powershell
# Terminal 2
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
# Terminal 1
uvicorn app.main:app --reload
```

```bash
# Terminal 2
python -m app.bot.main
```
