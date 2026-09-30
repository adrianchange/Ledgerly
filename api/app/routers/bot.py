import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_bot_token
from app.database import get_db
from app.models import Expense, LinkCode, User
from app.schemas import (
    BotExpenseIn,
    BotLinkIn,
    BotMonthIn,
    ExpenseOut,
    LinkCodeOut,
    MonthSummary,
    UserOut,
)
from app.services import default_spent_at, month_summary

router = APIRouter(tags=["telegram"])


@router.post("/api/link-codes", response_model=LinkCodeOut)
def create_link_code(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LinkCodeOut:
    code = secrets.token_hex(3).upper()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    row = LinkCode(user_id=user.id, code=code, expires_at=expires)
    db.add(row)
    db.commit()
    return LinkCodeOut(code=code, expires_at=expires)


@router.post("/api/bot/link", response_model=UserOut, dependencies=[Depends(require_bot_token)])
def bot_link(body: BotLinkIn, db: Session = Depends(get_db)) -> User:
    now = datetime.now(timezone.utc)
    link = (
        db.query(LinkCode)
        .filter(LinkCode.code == body.code.upper(), LinkCode.used_at.is_(None))
        .order_by(LinkCode.id.desc())
        .first()
    )
    if not link or link.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Invalid or expired link code")

    existing = db.query(User).filter(User.telegram_id == body.telegram_id).first()
    if existing and existing.id != link.user_id:
        raise HTTPException(status_code=400, detail="Telegram already linked to another account")

    user = db.get(User, link.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.telegram_id = body.telegram_id
    link.used_at = now
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/api/bot/expenses",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_bot_token)],
)
def bot_create_expense(body: BotExpenseIn, db: Session = Depends(get_db)) -> Expense:
    user = db.query(User).filter(User.telegram_id == body.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Telegram not linked. Use /start CODE from the web app.")
    expense = Expense(
        user_id=user.id,
        amount=body.amount,
        category=body.category,
        note=body.note,
        spent_at=default_spent_at(body.spent_at),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.post(
    "/api/bot/summary/month",
    response_model=MonthSummary,
    dependencies=[Depends(require_bot_token)],
)
def bot_month_summary(body: BotMonthIn, db: Session = Depends(get_db)) -> MonthSummary:
    user = db.query(User).filter(User.telegram_id == body.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Telegram not linked")
    today = datetime.now(timezone.utc).date()
    return month_summary(db, user.id, body.year or today.year, body.month or today.month)
