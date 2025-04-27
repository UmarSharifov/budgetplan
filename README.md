# BudgetPlan

Современное веб-приложение для управления личным бюджетом с футуристическим интерфейсом в стиле Tron.

## Особенности

- 🎯 Управление бюджетами по категориям (развлечения и питание)
- 📊 Отслеживание расходов в реальном времени
- 💰 Визуализация остатков бюджета
- 🎨 Современный интерфейс в стиле Tron
- 📱 Адаптивный дизайн
- ⚡ Быстрая работа благодаря асинхронному бэкенду

## Технологии

- Backend: FastAPI, SQLAlchemy
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (с возможностью перехода на PostgreSQL)
- UI Framework: Bootstrap 5

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/budgetplan.git
cd budgetplan
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для Linux/Mac:
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите приложение:
```bash
uvicorn __main__:app --reload
```

5. Откройте браузер и перейдите по адресу: http://localhost:8000

## Деплой

Проект готов к деплою на Render.com. Для деплоя:

1. Создайте аккаунт на [Render.com](https://render.com)
2. Создайте новый Web Service
3. Подключите ваш GitHub репозиторий
4. Настройте переменные окружения (если необходимо)
5. Запустите деплой

## Структура проекта

```
budgetplan/
├── __main__.py          # Основной файл приложения
├── database.py          # Конфигурация базы данных
├── models.py            # Модели данных
├── requirements.txt     # Зависимости проекта
├── Procfile            # Конфигурация для деплоя
├── runtime.txt         # Версия Python
├── templates/          # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   └── budgets.html
└── README.md           # Документация
```

## Лицензия

MIT

## Автор

Ваше имя 