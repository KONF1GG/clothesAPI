from pathlib import Path
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import UPLOAD_FOLDER
from models import Base, ClothesType, User, Session, engine

async def lifespan(app: FastAPI):
    print('START')

    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as session:
        # Данные для добавления в БД: категории и их типы
        types_data = {
            "Голова": ["Шапка", "Кепка", "Бандана", "Шляпа", "Тюбетейка", "Берет"],
            "Тело": ["Футболка", "Рубашка", "Пуловер", "Свитер", "Туника", "Платье", "Куртка", "Жакет", "Пальто"],
            "Руки": ["Перчатки", "Рукавицы", "Напульсники", "Манжеты"],
            "Ноги": ["Брюки", "Шорты", "Джинсы", "Леггинсы", "Юбка", "Тренировки"],
            "Стопы": ["Туфли", "Ботинки", "Кроссовки", "Сандалии", "Босоножки", "Ботфорты", "Шлепанцы"],
        }

        # Получаем существующие записи
        existing_types = await session.execute(select(ClothesType))
        existing_types = {f"{row.name}_{row.category}" for row in existing_types.scalars().all()}

        # Добавляем новые записи, если их нет
        for category_name, types in types_data.items():
            for type_name in types:
                key = f"{type_name}_{category_name}"
                if key not in existing_types:
                    session.add(ClothesType(name=type_name, category=category_name))

        await session.commit()  # Сохраняем изменения

    yield
    print('STOP')
