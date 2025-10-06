# lexi-backend

Jagriti API Wrapper — FastAPI backend that wraps Jagriti Consumer Courts portal APIs.

This README explains how to create and activate a Python virtual environment (venv) on Windows PowerShell, install dependencies from `requirements.txt`, and run the application locally with Uvicorn. Environment variables can be provided directly in your shell to override defaults in `app/config.py`.

## Prerequisites

- Git (optional, for cloning)

## 1) Create and activate a virtual environment (PowerShell)

From the project root (`C:\Users\vatsal\Desktop\blockchain\lexi-backend`):

```powershell
# Create venv in a folder named .venv (recommended)
python -m venv .venv

# Activate the venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# You should see (.venv) prefix in your prompt when activated
```

If you get an execution policy error when activating ("running scripts is disabled on this system"), run PowerShell as Administrator once and run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then re-open your PowerShell (or run the Activate.ps1 again).

## 2) Install dependencies

With the venv activated:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

(Optional) To pin or freeze dependencies after changes:

```powershell
pip freeze > requirements.txt
```

## 3) Configure environment variable overrides (optional)

All settings in `app/config.py` have sensible defaults. You only need to set environment variables if you want to override a value (for example to enable debug mode or change the Jagriti base URL).

## 4) Run the app (development)

With the venv activated and dependencies installed, from project root:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Open http://127.0.0.1:8000/docs to see the interactive API docs.

Alternatively you can run the module directly (the `if __name__ == "__main__"` entrypoint in `app/main.py`):
```

## Project structure

Below is the repository layout and a short description for each folder / file (__init__.py and __pycache__ entries are omitted):

```
.\                     - project root
├─ jagriti_api.log      - runtime log file (can be ignored or examined for debugging)
├─ Readme.md            - this README with setup instructions and project notes
├─ requirements.txt     - pinned Python dependencies for the project
└─ app/                 - main application package
   ├─ config.py         - application configuration and environment variable defaults
   ├─ main.py           - FastAPI app setup and entrypoint (mounts routes, runs uvicorn)
   ├─ api/              - HTTP API layer (routing)
   │  └─ routes/
   │     └─ cases.py    - API endpoints for case-related routes (request handling + response)
   ├─ models/           - Pydantic models used across the app
   │  ├─ requests.py    - request schemas / input models
   │  └─ responses.py   - response schemas / output models
   ├─ services/         - business logic and integrations
   │  ├─ cache_service.py   - caching helpers / abstraction layer
   │  ├─ case_service.py    - core case-related business logic (service layer)
   │  ├─ jagriti_client.py  - HTTP client wrapper that talks to Jagriti external APIs
   │  └─ mapper_service.py  - transforms and maps external Jagriti data to internal models
   └─ utils/            - small utilities and app helpers
      ├─ exceptions.py  - custom exceptions and error helpers
      └─ logging_config.py - logging configuration used by the app
```