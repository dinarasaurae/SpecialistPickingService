
# **Практическая работа 1.2. Настройка БД, SQLAlchemy и миграции через Alembic**

## **1. Цель работы**
Цель работы — подключить PostgreSQL к FastAPI, настроить ORM (SQLAlchemy) и выполнить миграции через Alembic.

## **2. Ход работы**

### **2.1 Установка зависимостей**
Устанавливаем необходимые библиотеки:
```sh
pip install fastapi[all] sqlalchemy psycopg2-binary alembic
```

---

### **2.2 Настройка подключения к БД**
Создаём файл `connection.py` для управления соединением с базой данных:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:123@localhost:5433/psychologists_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
- **`DATABASE_URL`** – строка подключения к PostgreSQL.
- **`engine`** – создаёт движок базы данных.
- **`SessionLocal`** – создаёт сессию для работы с БД.
- **`get_db()`** – функция-зависимость для работы с БД в FastAPI.

---

### **2.3 Создание моделей данных**
Файл `models.py`:

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel

Base = declarative_base()

psychologist_specialization = Table(
    "psychologist_specialization",
    Base.metadata,
    Column("psychologist_id", Integer, ForeignKey("psychologists_data.id"), primary_key=True),
    Column("specialization_id", Integer, ForeignKey("specializations.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, nullable=False)

    psychologist_data = relationship("PsychologistData", back_populates="user", uselist=False)

class PsychologistData(Base):
    __tablename__ = "psychologists_data"

    id = Column(Integer, primary_key=True, index=True)
    experience = Column(Integer, nullable=False)
    bio = Column(String)
    rating = Column(Float)
    price_per_hour = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="psychologist_data")
    specializations = relationship("Specialization", secondary=psychologist_specialization, back_populates="psychologists")

class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    psychologists = relationship("PsychologistData", secondary=psychologist_specialization, back_populates="specializations")
```
- **Связь "многие ко многим"** между `PsychologistData` и `Specialization`.
- **Связь "один ко многим"** между `User` и `PsychologistData`.

---

### **2.4 Настройка Alembic**
#### **Инициализация Alembic**
```sh
alembic init migrations
```
Создаются файлы конфигурации Alembic.

#### **Настройка `alembic.ini`**
Открываем `alembic.ini` и меняем:
```ini
sqlalchemy.url = postgresql://postgres:123@localhost:5433/psychologists_db
```

#### **Настройка `env.py`**
Добавляем в `env.py`:
```python
from models import Base
target_metadata = Base.metadata
```
Это позволит Alembic управлять миграциями.

---

### **2.5 Создание миграции**
Генерируем файл миграции:
```sh
alembic revision --autogenerate -m "initial migration"
```
Применяем миграцию:
```sh
alembic upgrade head
```

---

### **2.6 Реализация API в FastAPI**
Файл `main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from connection import get_db
from models import User, PsychologistData, Specialization

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="пользователь не найден")
    return user

@app.post("/user")
def create_user(user: User, db: Session = Depends(get_db)):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="пользователь не найден")
    db.delete(user)
    db.commit()
    return {"message": "пользователь удалён"}

@app.get("/specializations")
def get_specializations(db: Session = Depends(get_db)):
    return db.query(Specialization).all()

@app.post("/user/{user_id}/specialization/{spec_id}")
def add_specialization(user_id: int, spec_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "psychologist":
        raise HTTPException(status_code=400, detail="User is not a psychologist")
    
    specialization = db.query(Specialization).filter(Specialization.id == spec_id).first()
    if not specialization:
        raise HTTPException(status_code=404, detail="Specialization not found")

    user.psychologist_data.specializations.append(specialization)
    db.commit()
    return user

@app.delete("/user/{user_id}/specialization/{spec_id}")
def remove_specialization(user_id: int, spec_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "psychologist":
        raise HTTPException(status_code=400, detail="User is not a psychologist")
    
    specialization = db.query(Specialization).filter(Specialization.id == spec_id).first()
    if not specialization:
        raise HTTPException(status_code=404, detail="Specialization not found")

    user.psychologist_data.specializations.remove(specialization)
    db.commit()
    return {"message": "Specialization removed"}
```

---

### **2.7 Работа с БД через SQLAlchemy**
Файл `query.py`:

```python
from sqlalchemy.orm import Session
from connection import SessionLocal
from models import User

db: Session = SessionLocal()

new_user = User(
    email="murr@example.com",
    full_name="Meow Meow",
    phone="+123455590",
    role="psychologist"
)

db.add(new_user)
db.commit()
db.refresh(new_user)
print(f"Добавлен пользователь: {new_user.full_name}, ID: {new_user.id}")

db.close()
```
Этот код:
1. Создаёт нового пользователя.
2. Добавляет его в БД.
3. Фиксирует изменения (`commit`).
4. Освежает объект (`refresh`).
5. Закрывает сессию.

---

## **3. Вывод**
В ходе работы:
- Подключена **PostgreSQL** к **FastAPI**.
- Реализована **ORM-модель** с помощью **SQLAlchemy**.
- Настроены **миграции Alembic**.
- Созданы **CRUD API** для пользователей и специализаций.
```