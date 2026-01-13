from sqlalchemy import BigInteger, String, ForeignKey, Boolean, Date, Time, Integer, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(50))
    role: Mapped[bool] = mapped_column(Boolean)  # True - Teacher, False - Student

    test_results: Mapped[list["TestResult"]] = relationship(back_populates="user")

# Модель материала
class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(primary_key=True)
    theme: Mapped[str] = mapped_column(String(50))
    material: Mapped[str] = mapped_column(String(10000))
    image_url: Mapped[str] = mapped_column(String(200), nullable=True)  # Ссылка на изображение
    video_url: Mapped[str] = mapped_column(String(200), nullable=True)  # Ссылка на видео
    audio_url: Mapped[str] = mapped_column(String(200), nullable=True)  # Ссылка на аудио
    animation_url: Mapped[str] = mapped_column(String(200), nullable=True)  # Ссылка на анимацию
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)

# Модель результата теста
class TestResult(Base):
    __tablename__ = "test_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Внешний ключ на пользователя
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))  # Внешний ключ на тест
    test_date: Mapped[Date] = mapped_column(Date)  # Дата прохождения теста
    score: Mapped[int] = mapped_column(Integer)

    # Связь с пользователем
    user: Mapped["User"] = relationship(back_populates="test_results")
    # Связь с тестом
    test: Mapped["Test"] = relationship(back_populates="results")

# Модель теста
class Test(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Связь с вопросами
    questions: Mapped[list["Question"]] = relationship(back_populates="test")
    # Связь с результатами тестов
    results: Mapped[list["TestResult"]] = relationship(back_populates="test")

# Модель вопроса
class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[int] = mapped_column(Integer)  # Тип вопроса (например, 1 - выбор, 2 - текст)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))  # Внешний ключ на тест

    # Связь с тестом
    test: Mapped["Test"] = relationship(back_populates="questions")
    # Связь с ответами
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")

# Модель ответа
class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))  # Внешний ключ на вопрос
    text: Mapped[str] = mapped_column(String(50))
    pair_key: Mapped[str] = mapped_column(String(50), nullable=True)  # Ключ для пары (если применимо)
    pair_value: Mapped[str] = mapped_column(String(50), nullable=True)  # Значение для пары (если применимо)
    is_correct: Mapped[bool] = mapped_column(Boolean)

    # Связь с вопросом
    question: Mapped["Question"] = relationship(back_populates="answers")

class CurrentUser(Base):
    __tablename__ = "current_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ID текущего пользователя


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


