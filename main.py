from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import joinedload
from datetime import date, datetime
from typing import List
import os
from pydantic import BaseModel

from database import get_db, init_db
from models import Budget as BudgetModel, Expense as ExpenseModel, BudgetCategory
from schemas import Budget, BudgetCreate, Expense, ExpenseCreate

app = FastAPI()

# Подключаем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    # Получаем текущую дату
    today = date.today()
    
    # Находим текущий бюджет
    current_budget = None
    current_expenses = []
    
    # Получаем все бюджеты с предзагрузкой расходов
    result = await db.execute(
        select(BudgetModel)
        .options(joinedload(BudgetModel.expenses))
    )
    budgets = result.unique().scalars().all()
    
    # Находим текущий бюджет
    for budget in budgets:
        if budget.start_date <= today <= budget.end_date:
            current_budget = budget
            current_expenses = budget.expenses
            
            # Вычисляем расходы по категориям
            budget.entertainment_spent = sum(
                expense.amount for expense in current_expenses 
                if expense.category == BudgetCategory.ENTERTAINMENT
            )
            budget.food_spent = sum(
                expense.amount for expense in current_expenses 
                if expense.category == BudgetCategory.FOOD
            )
            budget.total_spent = budget.entertainment_spent + budget.food_spent
            
            # Вычисляем оставшиеся суммы
            budget.entertainment_remaining = budget.entertainment_amount - budget.entertainment_spent
            budget.food_remaining = budget.food_amount - budget.food_spent
            break
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_budget": current_budget,
            "current_expenses": current_expenses
        }
    )

@app.get("/budgets")
async def budgets_page(request: Request, db: AsyncSession = Depends(get_db)):
    # Получаем текущую дату
    today = date.today()
    
    # Получаем все бюджеты с предзагрузкой расходов
    result = await db.execute(
        select(BudgetModel)
        .options(joinedload(BudgetModel.expenses))
    )
    budgets = result.unique().scalars().all()
    
    # Для каждого бюджета вычисляем статистику
    for budget in budgets:
        # Вычисляем расходы по категориям
        budget.entertainment_spent = sum(
            expense.amount for expense in budget.expenses 
            if expense.category == BudgetCategory.ENTERTAINMENT
        )
        budget.food_spent = sum(
            expense.amount for expense in budget.expenses 
            if expense.category == BudgetCategory.FOOD
        )
        budget.total_spent = budget.entertainment_spent + budget.food_spent
        
        # Вычисляем оставшиеся суммы
        budget.entertainment_remaining = budget.entertainment_amount - budget.entertainment_spent
        budget.food_remaining = budget.food_amount - budget.food_spent
        
        # Определяем статус бюджета
        budget.is_current = budget.start_date <= today <= budget.end_date
        budget.is_future = budget.start_date > today
    
    # Вычисляем общую статистику
    total_budget = sum(budget.total_amount for budget in budgets)
    total_spent = sum(budget.total_spent for budget in budgets)
    total_entertainment_budget = sum(budget.entertainment_amount for budget in budgets)
    total_entertainment_spent = sum(budget.entertainment_spent for budget in budgets)
    total_food_budget = sum(budget.food_amount for budget in budgets)
    total_food_spent = sum(budget.food_spent for budget in budgets)
    
    return templates.TemplateResponse(
        "budgets.html",
        {
            "request": request,
            "budgets": budgets,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_entertainment_budget": total_entertainment_budget,
            "total_entertainment_spent": total_entertainment_spent,
            "total_food_budget": total_food_budget,
            "total_food_spent": total_food_spent
        }
    )

@app.post("/budgets/")
async def create_budget(
    start_date: date = Form(...),
    end_date: date = Form(...),
    entertainment_amount: float = Form(...),
    food_amount: float = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, что дата окончания позже даты начала
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="Дата окончания должна быть позже даты начала")
    
    # Проверяем, нет ли пересечения с существующими бюджетами
    result = await db.execute(
        select(BudgetModel).where(
            or_(
                and_(BudgetModel.start_date <= start_date, BudgetModel.end_date >= start_date),
                and_(BudgetModel.start_date <= end_date, BudgetModel.end_date >= end_date),
                and_(BudgetModel.start_date >= start_date, BudgetModel.end_date <= end_date)
            )
        )
    )
    existing_budget = result.scalar_one_or_none()
    if existing_budget:
        raise HTTPException(
            status_code=400,
            detail="Выбранный период пересекается с существующим бюджетом"
        )
    
    # Создаем новый бюджет
    new_budget = BudgetModel(
        start_date=start_date,
        end_date=end_date,
        entertainment_amount=entertainment_amount,
        food_amount=food_amount
    )
    db.add(new_budget)
    await db.commit()
    
    return RedirectResponse(url="/budgets", status_code=303)

class BudgetUpdate(BaseModel):
    start_date: date
    end_date: date
    amount: float
    category: str

@app.post("/budgets/delete")
async def delete_budget(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    data = await request.json()
    budget_id = data.get("budget_id")
    
    # Получаем бюджет
    result = await db.execute(select(BudgetModel).where(BudgetModel.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    
    # Удаляем бюджет (расходы удалятся автоматически благодаря cascade)
    await db.delete(budget)
    await db.commit()
    
    return JSONResponse({"status": "success"})

@app.post("/budgets/edit/{budget_id}")
async def edit_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Получаем бюджет
    result = await db.execute(select(BudgetModel).where(BudgetModel.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    
    # Проверяем, что дата окончания позже даты начала
    if budget_update.end_date <= budget_update.start_date:
        raise HTTPException(status_code=400, detail="Дата окончания должна быть позже даты начала")
    
    # Проверяем, нет ли пересечения с другими бюджетами той же категории
    result = await db.execute(
        select(BudgetModel).where(
            and_(
                BudgetModel.id != budget_id,
                BudgetModel.category == BudgetCategory(budget_update.category),
                or_(
                    and_(BudgetModel.start_date <= budget_update.start_date, BudgetModel.end_date >= budget_update.start_date),
                    and_(BudgetModel.start_date <= budget_update.end_date, BudgetModel.end_date >= budget_update.end_date),
                    and_(BudgetModel.start_date >= budget_update.start_date, BudgetModel.end_date <= budget_update.end_date)
                )
            )
        )
    )
    existing_budget = result.scalar_one_or_none()
    if existing_budget:
        raise HTTPException(
            status_code=400,
            detail="Выбранный период пересекается с существующим бюджетом той же категории"
        )
    
    # Обновляем бюджет
    budget.start_date = budget_update.start_date
    budget.end_date = budget_update.end_date
    budget.amount = budget_update.amount
    budget.category = BudgetCategory(budget_update.category)
    await db.commit()
    
    return JSONResponse({"status": "success"})

@app.post("/expenses/")
async def create_expense(
    date: date = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    budget_id: int = Form(...),
    category: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Получаем бюджет
    result = await db.execute(select(BudgetModel).where(BudgetModel.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    
    # Проверяем, что дата расхода входит в период бюджета
    if not (budget.start_date <= date <= budget.end_date):
        raise HTTPException(
            status_code=400,
            detail="Дата расхода должна быть в пределах периода бюджета"
        )
    
    # Получаем все расходы для бюджета
    result = await db.execute(
        select(ExpenseModel).where(ExpenseModel.budget_id == budget_id)
    )
    expenses = result.scalars().all()
    
    # Проверяем, что сумма расхода не превышает оставшийся бюджет для выбранной категории
    category_enum = BudgetCategory(category)
    if category_enum == BudgetCategory.ENTERTAINMENT:
        remaining = budget.entertainment_amount - sum(
            expense.amount for expense in expenses 
            if expense.category == BudgetCategory.ENTERTAINMENT
        )
        if amount > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Сумма расхода превышает оставшийся бюджет на развлечения ({remaining:,.2f} ₽)"
            )
    else:  # FOOD
        remaining = budget.food_amount - sum(
            expense.amount for expense in expenses 
            if expense.category == BudgetCategory.FOOD
        )
        if amount > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Сумма расхода превышает оставшийся бюджет на питание ({remaining:,.2f} ₽)"
            )
    
    # Создаем новый расход
    new_expense = ExpenseModel(
        date=date,
        description=description,
        amount=amount,
        budget_id=budget_id,
        category=category_enum
    )
    db.add(new_expense)
    await db.commit()
    
    return RedirectResponse(url="/", status_code=303)

# API endpoints
@app.post("/api/budgets/", response_model=Budget)
async def create_budget_api(
    budget: BudgetCreate,
    db: AsyncSession = Depends(get_db)
):
    db_budget = BudgetModel(
        start_date=budget.start_date,
        end_date=budget.end_date,
        amount=budget.amount,
        category=BudgetCategory(budget.category)
    )
    db.add(db_budget)
    await db.commit()
    await db.refresh(db_budget)
    return db_budget

@app.get("/api/budgets/", response_model=List[Budget])
async def get_budgets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetModel))
    budgets = result.scalars().all()
    return budgets

@app.post("/api/expenses/", response_model=Expense)
async def create_expense_api(
    expense: ExpenseCreate,
    db: AsyncSession = Depends(get_db)
):
    db_expense = ExpenseModel(
        date=expense.date,
        description=expense.description,
        amount=expense.amount,
        budget_id=expense.budget_id,
        category=BudgetCategory(expense.category)
    )
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense

@app.get("/api/expenses/", response_model=List[Expense])
async def get_expenses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExpenseModel))
    expenses = result.scalars().all()
    return expenses

if __name__ == "__main__":
    import uvicorn
    import asyncio
    
    # Инициализируем базу данных
    asyncio.run(init_db())
    
    # Запускаем приложение
    uvicorn.run(app, host="127.0.0.1", port=8000)