# User Service

## 🚀 Назначение сервиса

Микросервис для управления пользователями и их скрриптами. Основные функции:

- Регистрация пользователей и аутентификация (JWT)
- Управление балансом пользователей
- Управление скриптами и проектами (CRUD операции)

## 🏷 Архитектура и зависимости

### Технологический стек

- **Backend**: FastAPI 0.115.12 — высокопроизводительный веб-фреймворк для создания API.
- **Аутентификация**: PyJWT 2.10.1 — библиотека для работы с JSON Web Tokens.
- **Документация**: OpenAPI 3.0 (автоматически генерируется FastAPI).
- **База данных**: PostgreSQL (asyncpg 0.30.0) — асинхронный драйвер для PostgreSQL.
- **ORM**: SQLAlchemy 2.0.40 — инструмент для работы с реляционными базами данных.
- **ASGI-сервер**: Uvicorn 0.34.0 — сервер для запуска FastAPI-приложений.
- **Валидация данных**: Pydantic 2.11.3 — библиотека для валидации данных.
- **Тестирование**: Pytest 8.3.5 с поддержкой асинхронных тестов через pytest-asyncio 1.0.0.
- **Другие зависимости**: python-dotenv 1.1.0, httpx 0.28.1, bcrypt 4.3.0 и др.

### Взаимодействие с системой

- **Используемые внешние сервисы**: PostgreSQL.

## 📦 Подготовка
### Клонируйте репозиторий:

   ```bash
   git clone https://github.com/A-re-s/user-service.git
   cd user-service
   ```



## 🛠 Запуск сервиса

### Требования

- Python 3.12+
- Docker (для запуска с Docker)
- Файл `.env` в корне проекта с необходимыми переменными (см. раздел "⚙️ Настройка окружения").

### Локальный запуск
1. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate  # для Windows
   ```

2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```
3. Запустите сервис с помощью:

    ```bash
    make run
    ```


### Запуск с помощью Docker

1. Убедитесь, что у вас установлены Docker.

2. Запустите сервис:

   ```bash
   make docker-run #interactive mode
   make docker-run-detached #detached mode
   ```

Это запустит веб-сервис.

## ⚙️ Настройка окружения

Создайте файл `.env` в корне проекта:

```
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

SECRET_KEY=

PORT=
```

## 📚 API Документация

Документация API автоматически генерируется FastAPI и доступна по адресам:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 🧪 Тестирование

Для запуска тестов выполните:

```bash
make test
```