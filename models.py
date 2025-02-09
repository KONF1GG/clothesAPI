from config import DSN
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

engine = create_async_engine(
    DSN,
)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    
    clothes: Mapped[list['Clothes']] = relationship('Clothes', back_populates='user')
    outfits: Mapped[list['Outfit']] = relationship('Outfit', secondary='clothes_outfit', back_populates='users')

class ClothesType(Base):
    __tablename__ = 'clothes_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    clothes: Mapped[list['Clothes']] = relationship('Clothes', back_populates='clothes_type')

class Clothes(Base):
    __tablename__ = 'clothes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    size: Mapped[str] = mapped_column(String(50), nullable=True)
    price: Mapped[float] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Новое поле для фото
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    user: Mapped[User] = relationship('User', back_populates='clothes')

    clothes_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('clothes_type.id'))
    clothes_type: Mapped[ClothesType] = relationship('ClothesType', back_populates='clothes')

class Outfit(Base):
    __tablename__ = 'outfit'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    clothes: Mapped[list['Clothes']] = relationship('Clothes', secondary='clothes_outfit', back_populates='outfits')
    users: Mapped[list[User]] = relationship('User', secondary='clothes_outfit', back_populates='outfits')


class ClothesOutfit(Base):
    __tablename__ = 'clothes_outfit'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    outfit_id: Mapped[int] = mapped_column(Integer, ForeignKey('outfit.id'))
    clothes_id: Mapped[int] = mapped_column(Integer, ForeignKey('clothes.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    
    clothes: Mapped[Clothes] = relationship('Clothes', back_populates='outfits')
    outfit: Mapped[Outfit] = relationship('Outfit', back_populates='clothes')
    user: Mapped[User] = relationship('User', back_populates='outfits')

ORM_OBJECT = User | ClothesType | Clothes | Outfit | ClothesOutfit
ORM_CLASS = type(User), type(ClothesType), type(Clothes), type(Outfit), type(ClothesOutfit)
