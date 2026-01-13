from datetime import datetime, date
from sqlalchemy import select, BigInteger, distinct
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Test, Question, Answer, TestResult, CurrentUser

# Настройки подключения к базе данных
from database.models import async_session
from database.models import User, Material

# Создание нового пользователя
async def set_user(name: str, password: str, role: str):
    async with async_session() as session:
        if role == 'teacher':
            flag = 1
        elif role == 'student':
            flag = 0
        user = await session.scalar(select(User).where(User.name == name, User.password == password, User.role == flag))
        if not user:
            session.add(User(name=name, password=password, role=flag))
            await session.commit()

async def set_material(theme: str, material: str, image_url=None, video_url=None, audio_url=None, animation_url=None):
    async with async_session() as session:
        lection = await session.scalar(
            select(Material).where(Material.theme == theme, Material.material == material)
            # Material.image_url == image_url,Material.video_url == video_url,Material.audio_url == audio_url,Material.animation_url == animation_url
        )
        if not lection:
            session.add(
                Material(
                    theme=theme, material=material, image_url=image_url, video_url=video_url, audio_url=audio_url, animation_url=animation_url
                )
            )
            await session.commit()


async def get_user_by_username(name: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.name == name))
        return result.scalars().first()
    


async def update_material(material_id: int, field: str, value):
    async with async_session() as session:
        material = await session.get(Material, material_id)
        if material:
            setattr(material, field, value)
            await session.commit()


async def get_materials_by_theme(theme: str):
    async with async_session() as session:
        result = await session.execute(
            select(Material).where(Material.theme == theme)
        )
        return result.scalars().all()

async def get_all_themes():
    async with async_session() as session:
        result = await session.execute(select(distinct(Material.theme)))
        return [row[0] for row in result.fetchall()]
    



logger = logging.getLogger(__name__)



async def get_all_tests(async_session) -> list:
    async with async_session() as session:
        result = await session.execute(select(Test))
        tests = result.scalars().all()
        return tests
    

async def save_question(
    test_id: int,
    question_text: str,
    question_type: str,
    options: list = None,
    pairs: dict = None,
    correct_answer: str = None,
    async_session=None
):
    """
    Сохраняет вопрос и связанные с ним ответы в базу данных.
    """
    async with async_session() as session:
        # Определяем тип вопроса (1 - текст, 2 - множественный выбор, 3 - соответствие)
        type_mapping = {"text": 1, "multiple": 2, "matching": 3}
        question_type_int = type_mapping.get(question_type)

        # Создаем вопрос
        new_question = Question(
            name=question_text,
            type=question_type_int,
            test_id=test_id
        )
        session.add(new_question)
        await session.commit()
        await session.refresh(new_question)

        # Сохраняем варианты ответов
        if question_type == "multiple":
            for option in options:
                is_correct = option == correct_answer
                answer = Answer(
                    question_id=new_question.id,
                    text=option,
                    is_correct=is_correct
                )
                session.add(answer)

        elif question_type == "matching":
            for key, value in pairs.items():
                answer = Answer(
                    question_id=new_question.id,
                    text=f"{key}-{value}",  # Заполняем поле text
                    pair_key=key,
                    pair_value=value,
                    is_correct=True  # Все пары считаются правильными
                )
                session.add(answer)

        elif question_type == "text":
            answer = Answer(
                question_id=new_question.id,
                text=correct_answer,
                is_correct=True
            )
            session.add(answer)

        await session.commit()


async def create_test(name: str, async_session) -> int:
    """
    Создает новый тест в базе данных.
    Возвращает ID созданного теста.
    """
    async with async_session() as session:
        new_test = Test(name=name)
        session.add(new_test)
        await session.commit()
        await session.refresh(new_test)
        return new_test.id
    

async def get_test_results(test_id: int, async_session):
    async with async_session() as session:
        results = await session.execute(
            select(TestResult)
            .where(TestResult.test_id == test_id)
            .options(joinedload(TestResult.user), joinedload(TestResult.test))
        )
        return results.scalars().all()
    
async def get_all_results(async_session):
    async with async_session() as session:
        results = await session.execute(
            select(TestResult)
            .options(joinedload(TestResult.user), joinedload(TestResult.test))
        )
        return results.scalars().all()
    
async def save_test_result(user_id: int, test_id: int, score: int, async_session):
    """
    Сохраняет результат теста в базу данных.
    """
    async with async_session() as session:
        test_result = TestResult(
            user_id=user_id,
            test_id=test_id,
            test_date=date.today(),
            score=score
        )
        session.add(test_result)
        await session.commit()

async def get_user_by_username2(username: str, async_session):
    """
    Получает пользователя из базы данных по имени.
    Возвращает ID пользователя или None, если пользователь не найден.
    """
    async with async_session() as session:
        user = await session.execute(
            select(User).where(User.name == username)
        )
        user = user.scalars().first()
        return user.id if user else None
    
async def update_current_user(user_id: int, async_session):
    """
    Обновляет ID текущего пользователя в таблице current_user.
    Если записи нет, создает новую.
    """
    async with async_session() as session:
        current_user = await session.execute(select(CurrentUser))
        current_user = current_user.scalars().first()

        if current_user:
            current_user.user_id = user_id
        else:
            current_user = CurrentUser(user_id=user_id)
            session.add(current_user)

        await session.commit()
    

async def get_current_user(async_session):
    """
    Получает ID текущего пользователя из таблицы current_user.
    Возвращает None, если записи нет.
    """
    async with async_session() as session:
        current_user = await session.execute(select(CurrentUser))
        current_user = current_user.scalars().first()
        return current_user.user_id if current_user else None