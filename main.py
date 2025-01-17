import uvicorn # Импорт сервера для запуска FastAPI приложения
import datetime # Импорт модуля для работы с датами и временем
from fastapi import FastAPI, HTTPException, Depends 
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean #Компоненты для работы с БД через ORM
from sqlalchemy.orm import declarative_base # Импорт конструктора для создания базового класса моделей
from sqlalchemy.orm import sessionmaker, Session # Импорт компонентов для создания сессий работы с БД
from pydantic import BaseModel # Импорт базового класса для создания схем данных
from typing import Generator # Импорт типа Generator для аннотации типов

# Конфигурация базы данных SQLite
DATABASE_URL = "sqlite:///./users.db"

# Инициализация движка SQLAlchemy и сессии
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создание фабрики сессий
Base = declarative_base() # Создание базового класса для моделей

# Свойства таблицы User в базе данных
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=False, index=True, nullable=False)
    user_name = Column(String, nullable=True)
    user_surname = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    time_of_add = Column(DateTime, default=datetime.datetime.utcnow)
    is_actual = Column(Boolean, default=True)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Определение схемы пользователя (Мы определям свойства json-объекта)
class UserInfo(BaseModel):
    user_id: int
    user_name: str
    user_surname: str | None
    age: int | None
    height: int | None
    weight: float | None
    time_of_add: datetime.datetime
    is_actual: bool | None

    class Config:
        from_attributes = True

# Создаем объект приложения
app = FastAPI()

# Зависимость для предоставления сессии базы данных
def get_db() -> Generator[Session, None, None]: 
    db = SessionLocal() # Создание новой сессии
    try:
        yield db # Возврат сессии для использования в запрос
    finally:
        db.close() # Закрытие сессии после завершения запроса

# Эндпоинт для создания пользователя
@app.post("/users/", response_model=UserInfo)
async def create_user(user: UserInfo, db: Session = Depends(get_db)):
    if not user.is_actual: # Проверка, актуальна ли запись
        raise HTTPException(status_code=403, detail="Not actual record") # Ошибка, если запись не актуальна
    
    # Проверка, существует ли пользователь с таким же ID
    existing_users = db.query(User).filter(User.user_id == user.user_id, User.is_actual == True).all()
    for existing_user in existing_users:
        existing_user.is_actual = False  # Проверка, существует ли пользователь с таким же ID
        db.commit() # Сохраняем изменения в базе данных

    # Создание нового пользователя
    new_user = User(
        user_id=user.user_id,
        user_name=user.user_name,
        user_surname=user.user_surname,
        age=user.age,
        height=user.height,
        weight=user.weight,
        time_of_add=user.time_of_add,
        is_actual=user.is_actual,
    )
    db.add(new_user) # Добавление нового пользователя в сессию
    db.commit() # Сохранение изменений в базе данных
    db.refresh(new_user) # Обновление объекта новыми данными из базы
    return new_user  # Возврат созданного пользователя

# Эндпоинт для получения пользователя по ID
@app.get("/users/{user_id}", response_model=UserInfo)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    
    # Поиск пользователя по ID
    user = db.query(User).filter(User.user_id == user_id, User.is_actual == True).first()
    
    # Проверка, если пользователь не найден, вывести сообщение об ошибке
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Эндпоинт для удаления пользователя
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    
    # Поиск всех записей пользователя
    user_records = db.query(User).filter(User.user_id == user_id)
    
    # Проверка, если записи не найдены, вывести сообщение об ошибке
    if not user_records:
        raise HTTPException(status_code=404, detail="User not found")
    for user in user_records.all(): # Перебор всех записей пользователя
        db.delete(user)
    db.commit()
    
    # Возврат сообщения об успешном удалении
    return {"message": f"User with ID {user_id} has been marked as deleted."}

# Эндпоинт для обновления пользователя
@app.put("/users/{user_id}", response_model=UserInfo)
async def update_user(user_id: int, updated_user: UserInfo, db: Session = Depends(get_db)):
    
    # Поиск пользователя по ID
    user = db.query(User).filter(User.user_id == user_id, User.is_actual == True).first()
    
    # Проверка, если записи не найдены, вывести сообщение об ошибке
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
     
    # Обновление данных пользователя
    user.user_name = updated_user.user_name
    user.user_surname = updated_user.user_surname
    user.age = updated_user.age
    user.height = updated_user.height
    user.weight = updated_user.weight
    db.commit()
    db.refresh(user)
    return user

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Запуск сервера