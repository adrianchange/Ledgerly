from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models import Expense
from app.schemas import CategoryTotal, MonthSummary


def month_summary(db: Session, user_id: int, year: int, month: int) -> MonthSummary:
    rows = (
        db.query(Expense.category, func.coalesce(func.sum(Expense.amount), 0), func.count(Expense.id))
        .filter(
            Expense.user_id == user_id,
            extract("year", Expense.spent_at) == year,
            extract("month", Expense.spent_at) == month,
        )
        .group_by(Expense.category)
        .all()
    )
    by_category = [
        CategoryTotal(category=cat, total=Decimal(str(total)))
        for cat, total, _count in rows
    ]
    total = sum((c.total for c in by_category), Decimal("0"))
    count = sum(count for _cat, _total, count in rows)
    return MonthSummary(
        year=year,
        month=month,
        total=total,
        by_category=sorted(by_category, key=lambda c: c.total, reverse=True),
        count=count,
    )


def default_spent_at(value: date | None) -> date:
    return value or date.today()
