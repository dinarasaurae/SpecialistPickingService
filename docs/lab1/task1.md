# **Практическая работа 1.1. Создание базового приложения на FastAPI**

## **1. Цель работы**
Цель данной работы — разработка базового FastAPI-приложения, включающего в себя API для работы с пользователями и специализациями. В ходе выполнения работы требуется:
- Ознакомиться с основами **FastAPI**.
- Реализовать **CRUD API** для работы с пользователями и их специализациями.
- Использовать **Pydantic** для валидации входных данных.

---

### **Основные элементы**
1. **Объект FastAPI**  
```python
   from fastapi import FastAPI
   app = FastAPI()
```

2. **Реализация эндпоинтов**  
   ```python
   @app.get("/")
   def root():
       return {"message": "Добро пожаловать!"}
   ```
3. **Запуск сервера**  
   ```sh
   uvicorn main:app --reload
   ```

---

## **3. Ход работы**

### **3.1 Установка и настройка окружения**
1. **Создано виртуальное окружение**:
   ```sh
   python -m venv venv
   venv\Scripts\activate 
   ```
2. **FastAPI и Uvicorn**:
   ```sh
   pip install fastapi[all]
   ```

---

### **3.2 Создание структуры проекта**
```
/psychologists_service
    /temp_db.py          
    /models.py           
    /main.py            
```

---

### **3.3 Реализация временной базы данных**

```python
from models import RoleType

temp_db = [
    {
        "id": 1,
        "email": "seregapirat@gmail.com",
        "full_name": "Serega Pirat",
        "phone": "+1234567890",
        "created_at": "2023-03-01T12:00:00",
        "role": RoleType.psychologist.value,
        "psychologist_data": {
            "experience": 5,
            "bio": "Licensed psychologist with expertise in CBT.",
            "rating": 4.8,
            "price_per_hour": 100.00,
            "specializations": [
                {"id": 1, "name": "Cognitive Behavioral Therapy"},
                {"id": 2, "name": "Anxiety Disorders"}
            ]
        }
    },
    {
        "id": 2,
        "email": "dinaemae@gmail.com",
        "full_name": "Dina Bolnaya",
        "phone": "+1987654321",
        "created_at": "2023-05-10T15:30:00",
        "role": RoleType.client.value,
        "psychologist_data": None
    }
]
```

---

### **3.4 Создание моделей данных**
Для валидации данных используется **Pydantic**.  

```python
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RoleType(str, Enum):
    client = "client"
    psychologist = "psychologist"

class Specialization(BaseModel):
    id: int
    name: str

class PsychologistData(BaseModel):
    experience: int
    bio: str
    rating: float
    price_per_hour: float
    specializations: List[Specialization]

class User(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    created_at: datetime
    role: RoleType
    psychologist_data: PsychologistData | None = None
```

---

### **3.5 Разработка API в `main.py`**

#### **3.5.1 Получение списка пользователей**
```python
from fastapi import FastAPI, HTTPException
from models import User, Specialization
from typing import Optional, List
from temp_db import temp_db

app = FastAPI()

@app.get("/users", response_model=List[User])
def get_users() -> List[User]:
    return temp_db
```

#### **3.5.2 Получение пользователя по `id`**
```python
@app.get("/user/{user_id}", response_model=User)
def get_user(user_id: int) -> Optional[User]:
    return next((user for user in temp_db if user["id"] == user_id), None)
```

#### **3.5.3 Создание нового пользователя**
```python
@app.post("/user", response_model=User)
def add_user(user: User) -> User:
    temp_db.append(user.model_dump())
    return user
```

#### **3.5.4 Удаление пользователя**
```python
@app.delete("/user/delete/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(temp_db):
        if user["id"] == user_id:
            temp_db.pop(i)
            return {"status": 204, "message": "пользователь удалён"}
    raise HTTPException(status_code=404, detail="пользователь не найден")
```

#### **3.5.5 Обновление данных пользователя**
```python
@app.put("/user/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    for i, u in enumerate(temp_db):
        if u["id"] == user_id:
            temp_db[i] = user.model_dump()
            return user
    raise HTTPException(status_code=404, detail="не найден")
```

---

### **3.6 Работа со специализациями**
#### **3.6.1 Получение списка специализаций**
```python
@app.get("/specializations", response_model=List[Specialization])
def get_specializations():
    specializations = []
    for user in temp_db:
        if user["psychologist_data"]:
            specializations.extend(user["psychologist_data"]["specializations"])
    return specializations
```

#### **3.6.2 Добавление специализации психологу**
```python
@app.post("/user/{user_id}/specialization", response_model=User)
def add_specialization(user_id: int, specialization: Specialization):
    for user in temp_db:
        if user["id"] == user_id and user["role"] == "psychologist":
            user["psychologist_data"]["specializations"].append(specialization.dict())
            return user
    raise HTTPException(status_code=404, detail="Psychologist not found")
```

#### **3.6.3 Удаление специализации**
```python
@app.delete("/user/{user_id}/specialization/{specialization_id}")
def delete_specialization(user_id: int, specialization_id: int):
    for user in temp_db:
        if user["id"] == user_id and user["role"] == "psychologist":
            user["psychologist_data"]["specializations"] = [
                s for s in user["psychologist_data"]["specializations"] if s["id"] != specialization_id
            ]
            return {"status": 201, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Psychologist not found")
```