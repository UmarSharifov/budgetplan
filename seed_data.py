import asyncio
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models import Base, Budget, Expense

# Создаем асинхронный движок
engine = create_async_engine("sqlite+aiosqlite:///./budget.db", echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed_data():
    async with async_session() as session:
        # Создаем примеры бюджетов
        budgets = [
            Budget(
                amount=50000.0,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            ),
            Budget(
                amount=30000.0,
                start_date=date(2024, 4, 1),
                end_date=date(2024, 6, 30)
            )
        ]
        
        for budget in budgets:
            session.add(budget)
        
        await session.commit()
        
        # Получаем ID бюджетов
        result = await session.execute(text("SELECT id FROM budgets"))
        budget_ids = [row[0] for row in result.fetchall()]
        
        # Создаем примеры расходов
        expenses = [
            Expense(
                date=date(2024, 1, 15),
                description="Продукты",
                amount=2500.0,
                budget_id=budget_ids[0]
            ),
            Expense(
                date=date(2024, 1, 20),
                description="Коммунальные услуги",
                amount=5000.0,
                budget_id=budget_ids[0]
            ),
            Expense(
                date=date(2024, 4, 5),
                description="Одежда",
                amount=3000.0,
                budget_id=budget_ids[1]
            ),
            Expense(
                date=date(2024, 4, 15),
                description="Развлечения",
                amount=1500.0,
                budget_id=budget_ids[1]
            )
        ]
        
        for expense in expenses:
            session.add(expense)
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_data()) 