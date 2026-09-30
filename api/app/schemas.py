from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Category = Literal["food", "transport", "home", "leisure", "health", "other"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    telegram_id: str | None = None
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: Category = "other"
    note: str | None = Field(default=None, max_length=500)
    spent_at: date | None = None


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: Category | None = None
    note: str | None = Field(default=None, max_length=500)
    spent_at: date | None = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: str
    note: str | None
    spent_at: date
    created_at: datetime


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class MonthSummary(BaseModel):
    year: int
    month: int
    total: Decimal
    by_category: list[CategoryTotal]
    count: int


class LinkCodeOut(BaseModel):
    code: str
    expires_at: datetime
    bot_deep_link_hint: str = "In Telegram: /start CODE"


class BotExpenseIn(BaseModel):
    telegram_id: str = Field(min_length=1, max_length=64)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: Category = "other"
    note: str | None = Field(default=None, max_length=500)
    spent_at: date | None = None


class BotLinkIn(BaseModel):
    telegram_id: str = Field(min_length=1, max_length=64)
    code: str = Field(min_length=4, max_length=16)


class BotMonthIn(BaseModel):
    telegram_id: str = Field(min_length=1, max_length=64)
    year: int | None = None
    month: int | None = None
