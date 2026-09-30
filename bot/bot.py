"""Ledgerly Telegram bot — thin client over the FastAPI bot endpoints."""

from __future__ import annotations

import logging
import os
import re
from decimal import Decimal, InvalidOperation

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ledgerly-bot")

API_URL = os.getenv("LEDGERLY_API_URL", "http://127.0.0.1:8000").rstrip("/")
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# /gasto 12.50 café  OR  /gasto 12,50 transport metro
GASTO_RE = re.compile(
    r"^\s*(?P<amount>\d+(?:[.,]\d{1,2})?)\s*(?P<rest>.*)$",
    re.IGNORECASE,
)
CATEGORIES = {"food", "transport", "home", "leisure", "health", "other"}


def api_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {BOT_API_TOKEN}", "Content-Type": "application/json"}


async def api_post(path: str, payload: dict) -> httpx.Response:
    async with httpx.AsyncClient(timeout=20.0) as client:
        return await client.post(f"{API_URL}{path}", json=payload, headers=api_headers())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "Ledgerly bot.\n\n"
            "1) En la web genera un código de enlace\n"
            "2) Aquí: /start CODIGO\n"
            "3) Luego: /gasto 4.50 cafe\n"
            "4) Resumen: /mes"
        )
        return

    code = args[0].strip().upper()
    r = await api_post("/api/bot/link", {"telegram_id": str(update.effective_user.id), "code": code})
    if r.status_code == 200:
        await update.message.reply_text(f"Cuenta enlazada: {r.json().get('email')}. Ya puedes usar /gasto")
    else:
        detail = r.json().get("detail", r.text)
        await update.message.reply_text(f"No pude enlazar: {detail}")


async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    text = " ".join(context.args or []).strip()
    if not text:
        await update.message.reply_text("Uso: /gasto 12.50 cafe\nOpcional categoria: /gasto 3.20 transport metro")
        return

    m = GASTO_RE.match(text)
    if not m:
        await update.message.reply_text("No entendi el importe. Ejemplo: /gasto 4.50 cafe")
        return

    raw_amount = m.group("amount").replace(",", ".")
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation:
        await update.message.reply_text("Importe invalido")
        return

    rest = (m.group("rest") or "").strip()
    category = "other"
    note = rest
    parts = rest.split(maxsplit=1)
    if parts and parts[0].lower() in CATEGORIES:
        category = parts[0].lower()
        note = parts[1] if len(parts) > 1 else None

    payload = {
        "telegram_id": str(update.effective_user.id),
        "amount": str(amount),
        "category": category,
        "note": note or None,
    }
    r = await api_post("/api/bot/expenses", payload)
    if r.status_code == 201:
        data = r.json()
        await update.message.reply_text(
            f"OK {data['amount']} EUR · {data['category']}"
            + (f" · {data['note']}" if data.get("note") else "")
        )
    else:
        detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
        await update.message.reply_text(f"Error: {detail}")


async def mes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    r = await api_post("/api/bot/summary/month", {"telegram_id": str(update.effective_user.id)})
    if r.status_code != 200:
        detail = r.json().get("detail", r.text)
        await update.message.reply_text(f"Error: {detail}")
        return
    data = r.json()
    lines = [f"Mes {data['month']}/{data['year']}: {data['total']} EUR ({data['count']} gastos)"]
    for row in data.get("by_category") or []:
        lines.append(f"· {row['category']}: {row['total']}")
    await update.message.reply_text("\n".join(lines) if lines else "Sin gastos este mes")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in bot/.env")
    if not BOT_API_TOKEN:
        raise SystemExit("Set BOT_API_TOKEN in bot/.env (same as API)")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gasto", gasto))
    app.add_handler(CommandHandler("mes", mes))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    log.info("Bot starting against %s", API_URL)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
