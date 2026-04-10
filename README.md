# VolonterUA Backend (V1)

## 📌 Overview
VolonterUA — це бекенд API для волонтерської платформи, де користувачі можуть створювати запити на допомогу, пропонувати допомогу та керувати процесом виконання.

Стек:
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Pytest

---

## ⚙️ Setup

### 1. Clone repository
git clone git@github.com:UserKostia/VolonterUA.git
cd VolonterUA

---

### 2. Install dependencies

Рекомендовано (Poetry):
poetry install

Альтернатива (pip):
pip install -r requirements.txt

---

### 3. Environment variables

Створи файл `.env` у корені проєкту:

DATABASE_URL=postgresql+asyncpg://name@localhost:5432/volonterua
DATABASE_URL_SYNC=postgresql+psycopg2://name@localhost:5432/volonterua

SECRET_KEY=SUPER_SECRET_KEY_CHANGE_ME
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

Примітки:
- Використовуй Gmail App Password
- PostgreSQL має бути запущений
- База даних повинна існувати

---

### 4. Run migrations

alembic upgrade head

---

### 5. Run server

uvicorn app.main:app --reload

---

## 📡 API Documentation

http://localhost:8000/docs

---

## 🧠 Architecture

- Service layer (business logic)
- Repository layer (DB access)
- Pydantic schemas
- Separation of concerns

---

## 🧪 Run tests

pytest app/tests/unit -v

---

## 📌 Notes

- Async SQLAlchemy
- Pagination
- Custom exceptions
- Unit tests coverage

---
