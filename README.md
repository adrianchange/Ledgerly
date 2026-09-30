# Ledgerly

> Gastos personales por **web** y **Telegram**.  
> Angular 19 · FastAPI · Python bot · JWT · SQLite/Postgres

Monorepo de portfolio: un solo dominio, tres capas (front / API / bot).

---

## Qué es

**Ledgerly** permite registrar gastos desde un panel Angular o escribiendo al bot de Telegram (`/gasto 4.50 cafe`). Misma API, mismas categorías, resumen del mes.

| Pieza | Carpeta | Stack |
|-------|---------|-------|
| API | `api/` | FastAPI, SQLAlchemy, JWT, OpenAPI |
| Web | `web/` | Angular 19 standalone, reactive forms |
| Bot | `bot/` | python-telegram-bot → endpoints `/api/bot/*` |

---

## Arquitectura

```
Telegram bot ──┐
               ├──► FastAPI (JWT web + BOT_API_TOKEN)
Angular web ───┘         │
                         └── SQLite (dev) / Postgres (prod)
```

1. Te registras en la web.
2. Generas un **código de enlace** (15 min).
3. En Telegram: `/start CODIGO`.
4. `/gasto 12.50 food cafe` o `/mes`.

---

## Arranque local

### API

```bash
cd api
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

- Health: http://127.0.0.1:8000/api/health  
- Swagger: http://127.0.0.1:8000/docs  

Tests:

```bash
cd api
.venv\Scripts\python -m pytest -q
```

### Web

```bash
cd web
npm install
npm start
```

Abre http://localhost:4200 — el proxy apunta a la API en `environment.ts`.

### Bot

1. Crea un bot con [@BotFather](https://t.me/BotFather) y copia el token.
2. Usa el **mismo** `BOT_API_TOKEN` que en `api/.env`.

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edita TELEGRAM_BOT_TOKEN, BOT_API_TOKEN, LEDGERLY_API_URL
python bot.py
```

---

## API (resumen)

| Método | Ruta | Auth |
|--------|------|------|
| POST | `/api/auth/register` | — |
| POST | `/api/auth/login` | — |
| GET | `/api/auth/me` | JWT |
| GET/POST | `/api/expenses` | JWT |
| GET | `/api/expenses/summary/month` | JWT |
| POST | `/api/link-codes` | JWT |
| POST | `/api/bot/link` | Bot token |
| POST | `/api/bot/expenses` | Bot token |
| POST | `/api/bot/summary/month` | Bot token |

Categorías: `food` · `transport` · `home` · `leisure` · `health` · `other`

---

## Docker (API)

```bash
docker compose up --build
```

---

## Roadmap

- Deploy demo (Railway API + Vercel web)
- Postgres en producción
- Presupuestos mensuales / multi-moneda
- Más tests e2e

---

## Autor

[adrianchange](https://github.com/adrianchange) · portfolio project
