# CareVanta

Digital healthcare platform for patients, doctors, clinic staff, lab technicians, and pharmacists. It covers doctor discovery, appointments, telehealth visits, clinical records, prescribing, labs, billing, insurance, messaging, and support.

## Stack

Django REST API and a React TypeScript single-page app.

## Layout

- `backend/` — Django API
- `frontend/` — React client

## Local setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Use PostgreSQL and Redis when the project expects them. Copy `.env.example` to `.env` where an example file is present, and keep real secrets out of git.

## License

Released under the [MIT License](LICENSE).
