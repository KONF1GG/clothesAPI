from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Base, ClothesType, User, Session, engine

async def lifespan(app: FastAPI):
    print('START')

    # Создаем таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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

        # Добавляем типы одежды с категориями
        for category_name, types in types_data.items():
            for type_name in types:
                # Создаем запись типа одежды с категорией
                new_clothes_type = ClothesType(name=type_name, category=category_name)
                session.add(new_clothes_type)

            await session.commit()  # Сохраняем типы одежды

        # Добавление пользователя, если его еще нет
        user = User(
            username="leo",
            firstname="Леонтий",
            lastname="Крохалев",
            email="krokxa228@gmail.com",
            password="12345678"
        )
        existing_user = await session.execute(
            select(User).filter(User.username == user.username)
        )
        existing_user = existing_user.scalar_one_or_none()

        if not existing_user:
            session.add(user)
            await session.commit()

    yield
    print('STOP')
