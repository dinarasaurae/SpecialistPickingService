# **Практическая работа 1.3. Реализация миграций в FastAPI с SQLAlchemy и Alembic**
## **1. Цель работы**
Настройка Alembic, добавление нового поля в таблицу для миграции, использование `.env` для безопасного хранения данных БД, обновление `alembic.ini`, чтобы использовать переменные окружения

---

### **2.1 Установка зависимостей**
```sh
pip install alembic python-dotenv
``` 
**`python-dotenv`** – позволяет загружать переменные окружения из `.env` файла.

---

### **2.1 Инициалтзация Alembic**
```sh
alembic init migrations
```
Это создаст в корне проекта каталог `migrations/` со следующей структурой:
```
/migrations
├── versions/       # Каталог с файлами миграций
├── env.py          # Настройки подключения к БД
├── README          # Информация о Alembic
├── script.py.mako  # Шаблон новых миграций
alembic.ini         # Конфигурация Alembic
```

### **3.1 Добавление `.env` в корень проекта**
Создан **`.env`**:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb
```

### **3.2 Обновление `connection.py`**
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Подключение к БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
```
**`DATABASE_URL` не хранится в коде**, а загружается из `.env`.

### **3.3 Обновление `alembic.ini`**
В `alembic.ini`:
```ini
sqlalchemy.url = postgresql://postgres:password@localhost:5432/mydb
```
**На:**
```ini
sqlalchemy.url = %(DATABASE_URL)s
```
Теперь **URL будет загружаться из переменной окружения**.

---
### **4 Обновление `env.py`**
```python
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from models import Base  

# переменные окружения
load_dotenv()
config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# логирование Alembic
fileConfig(config.config_file_name)

# метаданные моделей
target_metadata = Base.metadata

def run_migrations_offline():
    """Миграции в offline-режиме (без подключения к БД)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Миграции в online-режиме (с подключением к БД)"""
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```
Alembic **читает URL из `.env`** и **видит SQLAlchemy-модели**.


### **5.1 Обновление `models.py`**
Добавление   поле `age` в `UserDB`:
```python
from sqlalchemy import Column, Integer, String
from connection import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, nullable=False)
    age = Column(Integer, nullable=True)  # Новое поле
```

### **5.2 Генерация миграции**
```sh
alembic revision --autogenerate -m "Добавлено поле age в users"
```
**Alembic создаст новый файл в `migrations/versions/`**:
```
migrations/versions/202403061200_add_age_field.py
```
### **5.3 Проверка**
```python
from alembic import op
import sqlalchemy as sa

# ID ревизии
revision = '202403061200'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('users', 'age')
```
**`upgrade()`** добавляет поле `age`.  
**`downgrade()`** удаляет его при откате.

### **5.4 Применение миграции**
```sh
alembic upgrade head
```
### **6 Откат последней миграции:**
```sh
alembic downgrade -1
```
### **7.1 Создание `.gitignore`**
```
.env
```
✔ Теперь `.env` **не попадёт в Git**.

### **7.2 Запуск FastAPI с `.env`**
```sh
uvicorn main:app --reload
```
