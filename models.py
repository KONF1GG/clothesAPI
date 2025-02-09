from datetime import datetime
from config import DSN
from sqlalchemy import Integer, String, ForeignKey, Text, DateTime, CheckConstraint
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import MetaData

engine = create_async_engine(DSN, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    metadata = MetaData()

class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint('length(password) >= 8', name='password_min_length'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    
    clothes: Mapped[list['Clothes']] = relationship('Clothes', back_populates='user')
    outfits: Mapped[list['Outfit']] = relationship('Outfit', back_populates='user')

class ClothesType(Base):
    __tablename__ = 'clothes_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    clothes: Mapped[list['Clothes']] = relationship('Clothes', back_populates='type')

class Clothes(Base):
    __tablename__ = 'clothes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), index=True)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey('clothes_type.id'))
    image_url: Mapped[str] = mapped_column(String(255))

    type: Mapped['ClothesType'] = relationship('ClothesType', back_populates='clothes')
    user: Mapped['User'] = relationship('User', back_populates='clothes')
    outfits: Mapped[list['Outfit']] = relationship('Outfit', secondary='clothes_outfit', back_populates='clothes')

class Outfit(Base):
    __tablename__ = 'outfit'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), index=True)

    user: Mapped['User'] = relationship('User', back_populates='outfits')
    clothes: Mapped[list['Clothes']] = relationship('Clothes', secondary='clothes_outfit', back_populates='outfits')

class ClothesOutfit(Base):
    __tablename__ = 'clothes_outfit'

    outfit_id: Mapped[int] = mapped_column(ForeignKey('outfit.id'), primary_key=True)
    clothes_id: Mapped[int] = mapped_column(ForeignKey('clothes.id'), primary_key=True)

ORM_OBJECT = User | ClothesType | Clothes | Outfit | ClothesOutfit
ORM_CLASS = type(User), type(ClothesType), type(Clothes), type(Outfit), type(ClothesOutfit)
