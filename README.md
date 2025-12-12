<!-- # Furniture Factory — FastAPI + SQLite

## Что это
Подсистема для работы с продукцией мебельной компании:
- просмотр/редактирование продукции;
- список цехов по продукту и расчет времени изготовления;
- расчет сырья с учетом коэффициентов и потерь.

## Запуск
```bash
pip install -r requirements.txt
python create_bd.py      # создаст и заполнит furniture_production.db из CSV в папке data
python run.py            # стартует сервер на http://127.0.0.1:8000
# или
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Стек
- FastAPI
- SQLite + SQLAlchemy
- Pandas (импорт CSV)
- Ванильные HTML/CSS/JS (главная страница `/`)

## Основные эндпоинты
- `GET /products` — список продукции с временем изготовления
- `POST /products` — создать продукт
- `PUT /products/{id}` — обновить продукт
- `DELETE /products/{id}` — удалить
- `GET /products/{id}/workshops` — цеха для продукта
- `GET /products/{id}/production_time` — время изготовления
- `GET /product-types` — типы продукции (справочник)
- `GET /materials` — материалы (справочник)
- `POST /calculate_raw_material` — расчет требуемого сырья

## Структура
```
backend/
  main.py        # FastAPI
  models.py      # SQLAlchemy модели
  schemas.py     # Pydantic схемы
  database.py    # подключение к SQLite
frontend/
  index.html     # главная страница
  styles.css
  app.js
data/            # CSV из задания
create_bd.py     # создание и наполнение БД
run.py           # удобный запуск
requirements.txt
```

## Как это связано с ТЗ
- Часть 1: БД в 3НФ, загрузка данных из CSV, ER-схема отражена в таблицах/ключах.
- Часть 2: Алгоритм времени изготовления (сумма времени по цехам) и API.
- Часть 3: UI: хедер, сайдбар, таблицы с действиями, форма с валидацией, уведомления, футер.
- Часть 4: Список цехов для продукта, расчет сырья с учетом потерь и коэффициентов.
# Система управления продукцией мебельной компании

## Описание проекта

Веб-приложение для управления продукцией мебельной компании с возможностью:
- Просмотра и управления списком продукции
- Просмотра цехов для производства продукции
- Расчёта необходимого количества сырья для производства

## Структура проекта

```
Furniture_factory/
├── backend/              # Backend на FastAPI
│   ├── __init__.py
│   ├── main.py          # Основной файл API
│   ├── models.py        # SQLAlchemy модели
│   ├── schemas.py       # Pydantic схемы
│   └── database.py      # Настройка БД
├── frontend/            # Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/                # CSV файлы с данными для импорта
│   ├── Material_type_import.csv
│   ├── Product_type_import.csv
│   ├── Product_workshops_import.csv
│   ├── Products_import.csv
│   └── Workshops_import.csv
├── create_bd.py         # Скрипт создания и заполнения БД
├── requirements.txt     # Зависимости Python
└── README.md           # Этот файл
```

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Создание базы данных

Запустите скрипт для создания и заполнения базы данных:

```bash
python create_bd.py
```

Это создаст файл `furniture_production.db` с данными из CSV файлов.

### 3. Запуск backend сервера

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Или из корневой директории:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Открытие приложения

Откройте браузер и перейдите по адресу:
```
http://127.0.0.1:8000
```

## Использование

### Страница "Продукция"
- Просмотр списка всей продукции
- Добавление нового продукта (кнопка "Добавить продукт")
- Редактирование продукта (кнопка "Редактировать")
- Удаление продукта (кнопка "Удалить")

### Страница "Цеха и сырьё"
- Выбор продукта из выпадающего списка
- Просмотр цехов для производства выбранного продукта
- Расчёт необходимого количества сырья для производства

## API Endpoints

### Продукция
- `GET /products` - Получить список всех продуктов
- `POST /products` - Создать новый продукт
- `PUT /products/{product_id}` - Обновить продукт
- `DELETE /products/{product_id}` - Удалить продукт

### Цеха
- `GET /products/{product_id}/workshops` - Получить список цехов для продукта
- `GET /products/{product_id}/production_time` - Получить общее время изготовления

### Справочники
- `GET /product-types` - Получить список типов продуктов
- `GET /materials` - Получить список материалов

### Расчёт сырья
- `POST /calculate_raw_material` - Рассчитать необходимое количество сырья

## Технологии

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **База данных**: SQLite

## База данных

База данных состоит из следующих таблиц:
- `ProductTypes` - Типы продукции
- `Materials` - Типы материалов
- `Workshops` - Цеха
- `Products` - Продукция
- `ProductWorkshops` - Связь продукции и цехов

Все таблицы связаны внешними ключами с обеспечением ссылочной целостности. -->
