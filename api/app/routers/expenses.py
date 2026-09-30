from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Expense, User
from app.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate, MonthSummary
from app.services import default_spent_at, month_summary

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Expense]:
    q = db.query(Expense).filter(Expense.user_id == user.id)
    if year is not None:
        from sqlalchemy import extract

        q = q.filter(extract("year", Expense.spent_at) == year)
        if month is not None:
            q = q.filter(extract("month", Expense.spent_at) == month)
    return q.order_by(Expense.spent_at.desc(), Expense.id.desc()).limit(200).all()


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    body: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Expense:
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


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    body: ExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Expense:
    expense = db.get(Expense, expense_id)
    if not expense or expense.user_id != user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    expense = db.get(Expense, expense_id)
    if not expense or expense.user_id != user.id:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()


@router.get("/summary/month", response_model=MonthSummary)
def summary_month(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MonthSummary:
    today = date.today()
    y = year or today.year
    m = month or today.month
    return month_summary(db, user.id, y, m)
