import datetime
import uuid
from config import DSN
from sqlalchemy import CHAR, UUID, Integer, String, ForeignKey, Text, DateTime, CheckConstraint, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData

# Создание асинхронного движка и сессии
engine = create_async_engine(DSN, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

# Базовый класс
class Base(DeclarativeBase):
    metadata = MetaData()

# Модель пользователя
class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint('length(password) >= 8', name='password_min_length'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=True, index=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    tokens: Mapped[list['Token']] = relationship('Token', lazy='joined', back_populates='user')
    clothes: Mapped[list['Clothes']] = relationship(
        'Clothes', back_populates='user', cascade="all, delete", lazy="selectin"
    )
    outfits: Mapped[list['Outfit']] = relationship(
        'Outfit', back_populates='user', cascade="all, delete", lazy="selectin"
    )

class Token(Base):
    __tablename__ = 'token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[UUID] = mapped_column(CHAR(36), default=lambda: str(uuid.uuid4()), nullable=False)
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    user: Mapped[User] = relationship('User', lazy='joined', back_populates='tokens')


# Тип одежды
class ClothesType(Base):
    __tablename__ = 'clothes_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    clothes: Mapped[list['Clothes']] = relationship(
        'Clothes', back_populates='type', lazy="selectin"
    )

# Одежда
class Clothes(Base):
    __tablename__ = 'clothes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id', ondelete="CASCADE"), index=True, nullable=False
    )
    type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clothes_type.id', ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(255))

    type: Mapped['ClothesType'] = relationship(
        'ClothesType', back_populates='clothes', lazy="joined"
    )
    user: Mapped['User'] = relationship(
        'User', back_populates='clothes', lazy="joined"
    )
    outfits: Mapped[list['Outfit']] = relationship(
        'Outfit', secondary='clothes_outfit', back_populates='clothes', lazy="selectin"
    )

# Образы
class Outfit(Base):
    __tablename__ = 'outfit'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id', ondelete="CASCADE"), index=True, nullable=False
    )

    user: Mapped['User'] = relationship(
        'User', back_populates='outfits', lazy="joined"
    )
    clothes: Mapped[list['Clothes']] = relationship(
        'Clothes', secondary='clothes_outfit', back_populates='outfits', lazy="selectin"
    )

# Таблица связи одежда-образ
class ClothesOutfit(Base):
    __tablename__ = 'clothes_outfit'

    outfit_id: Mapped[int] = mapped_column(ForeignKey('outfit.id', ondelete="CASCADE"), primary_key=True)
    clothes_id: Mapped[int] = mapped_column(ForeignKey('clothes.id', ondelete="CASCADE"), primary_key=True)

# Объекты ORM
ORM_OBJECT = User | ClothesType | Clothes | Outfit | ClothesOutfit | Token
ORM_CLASS = type(User), type(ClothesType), type(Clothes), type(Outfit), type(ClothesOutfit) | type(Token)
