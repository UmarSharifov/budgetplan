from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base
import enum

class BudgetCategory(enum.Enum):
    ENTERTAINMENT = "entertainment"
    FOOD = "food"

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    entertainment_amount = Column(Float, nullable=False)
    food_amount = Column(Float, nullable=False)
    
    # Отношение к расходам
    expenses = relationship("Expense", back_populates="budget", cascade="all, delete-orphan")

    @property
    def total_amount(self):
        return self.entertainment_amount + self.food_amount

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    category = Column(Enum(BudgetCategory), nullable=False)
    
    # Отношение к бюджету
    budget = relationship("Budget", back_populates="expenses") 