from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from models import BudgetCategory

class ExpenseBase(BaseModel):
    date: date
    description: str
    amount: float
    category: BudgetCategory

class ExpenseCreate(ExpenseBase):
    budget_id: int

class Expense(ExpenseBase):
    id: int
    budget_id: int

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    start_date: date
    end_date: date
    entertainment_amount: float
    food_amount: float

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    total_spent: float = 0
    entertainment_spent: float = 0
    food_spent: float = 0
    entertainment_remaining: float = 0
    food_remaining: float = 0
    is_current: bool = False
    is_future: bool = False
    expenses: List[Expense] = []

    class Config:
        from_attributes = True 