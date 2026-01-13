from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder
from sqlalchemy import select, delete, distinct
from database.models import Test, Question, Answer, Material
from database.models import async_session

import app.keyboards as kb
from database.requests import set_user, get_user_by_username, set_material, update_material
from database.requests import  get_materials_by_theme, get_all_tests, get_user_by_username2, update_current_user, get_current_user
from database.requests import get_all_themes, create_test, get_test_results, get_all_results, save_test_result

from database.requests import save_question  # Импортируем функцию из requests.py

router = Router()


class Capitals(StatesGroup):
    sign_type = State()  # Выбор: вход или регистрация
    status = State()     # Выбор роли (преподаватель или студент)
    login = State()      # Ввод логина
    password = State()   # Ввод пароля

    add_material_theme = State()  # Ввод темы материала
    add_material_text = State()   # Ввод текста материала
    add_material_media = State()  # Загрузка медиафайлов

    edit_material_select = State()  # Выбор материала для редактирования
    edit_material_field = State()   # Выбор поля для изменения
    edit_material_value = State()
    edit_material_value2 = State()

    add_test_name = State()  # Ввод названия теста
    add_question_type = State()  # Выбор типа вопроса
    add_question_text = State()  # Ввод текста вопроса
    add_answer_text = State()  # Ввод текстового ответа
    add_multiple_choice_options = State()  # Ввод вариантов ответа (множественный выбор)
    add_correct_option = State()  # Ввод правильного варианта (множественный выбор)
    add_matching_pairs = State()  # Ввод пар для вопроса на соответствие
        # Редактирование теста
    edit_test_select = State()  # Выбор теста для редактирования
    edit_question_select = State()  # Выбор вопроса для редактирования
    edit_question_field = State()  # Выбор поля для изменения (текст вопроса, тип, ответы)
    edit_question_value = State()  # Ввод нового значения для выбранного поля
    delete_question_confirm = State()  # Подтверждение удаления вопроса
    edit_answer_select = State()
    edit_answer_value = State()
    # Удаление теста
    delete_test_select = State()  # Выбор теста для удаления
    delete_test_confirm = State()  # Подтверждение удаления теста

    answer_text_question = State()  # Ответ на текстовый вопрос
    answer_multiple_choice_question = State()  # Ответ на вопрос с множественным выбором
    answer_matching_question = State()  # Ответ на вопрос на соответствие
    add_question_to_test_select = State()
    add_test_from_text= State()
    # Выбор действия студента
    student_action = State()
    current_id = State()

@router.message(CommandStart())  # /start
async def b_start(message: Message):
    await message.answer(
        "👋 Привет! Это обучающая система для учителя и ученика 🎓",
        reply_markup=kb.login
    )


@router.callback_query(F.data == "main_menu_t")
async def main_menu(callback: CallbackQuery):
    await callback.message.answer(
        "🧑‍🏫 Выберите ваше действие",
        reply_markup=await kb.choose_teacher_action()
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu_s")
async def main_menu(callback: CallbackQuery):
    await callback.message.answer(
        "🎓 Выберите ваше действие",
        reply_markup=await kb.choose_student_action()
    )
    await callback.answer()


@router.message(F.text == "🔐 Войти или зарегистрироваться") 
async def start_signing(message: Message, state: FSMContext):
    await state.set_state(Capitals.sign_type)
    await message.answer(
        "🔐 Зарегистрируйтесь или войдите",
        reply_markup=await kb.choose_choice()
    )



@router.message(F.text == "🚪 Выйти из аккаунта")  # Кнопка выйти
async def start_signing(message: Message, state: FSMContext):
    await state.set_state(Capitals.sign_type)
    await message.answer("Вы успешно вышли из аккаунта", reply_markup=kb.login)
    await message.answer(
        "🚪 Зарегистрируйтесь или войдите",
        reply_markup=await kb.choose_choice()
    )
    

@router.callback_query(Capitals.sign_type)
async def sign_in_or_up(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]

    if action in ('in', 'up'):
        await state.update_data(sign_type=action)

    await state.set_state(Capitals.status)
    await callback.message.answer(
        "🎭 Выберите вашу роль:",
        reply_markup=await kb.choose_status()
    )
    await callback.answer()


@router.callback_query(Capitals.status)
async def choose_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data
    await state.update_data(status=role)
    data = await state.get_data()
    sign_type = data.get('sign_type')

    if sign_type == 'in':  # Если выбран вход
        await callback.message.answer("👤 Введите ваше ФИ:")
        await state.set_state(Capitals.login)

    elif sign_type == 'up':  # Если выбрана регистрация
        await callback.message.answer("📝 Введите ваше ФИ:")
        await state.set_state(Capitals.login)

    await callback.answer()


@router.message(Capitals.login)  # Ввод логина
async def process_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)  # Сохраняем логин в состояние
    await message.answer("🔐 Введите ваш пароль:")
    await state.set_state(Capitals.password)  # Переходим к вводу пароля


@router.message(Capitals.password)  # Ввод пароля
async def process_password(message: Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    sign_type = data.get('sign_type')
    role = data.get('status')  # Роль, выбранная пользователем (teacher/student)
    login = data.get('login')

    if sign_type == 'in':  # Если выбран вход
        user = await get_user_by_username(login)
        if user and user.password == password:  # Проверяем логин и пароль
            # Проверяем, соответствует ли роль пользователя выбранной роли
            if role == "teacher" and user.role == 1:  # Преподаватель
                await message.answer("🎉 Вы успешно вошли как учитель!", reply_markup=kb.logout)
                await message.answer(
                    "🧠 Выберите ваше действие",
                    reply_markup=await kb.choose_teacher_action()
                )
            elif role == "student" and user.role == 0:  # Ученик
                await message.answer("🎓 Вы успешно вошли как ученик!", reply_markup=kb.logout)
                await update_current_user(user.id, async_session)
                await message.answer(
                    "📚 Выберите ваше действие",
                    reply_markup=await kb.choose_student_action()
                )
            else:
                await message.answer("⚠️ Неверная роль для данного аккаунта.")
        else:
            await message.answer("❌ Неверное ФИ или пароль.")

    elif sign_type == 'up':  # Если выбрана регистрация
        existing_user = await get_user_by_username(login)
        if existing_user:
            await message.answer("🚫 Пользователь с таким ФИ уже существует.")
        else:
            # Регистрация нового пользователя
            await set_user(name=login, password=password, role=role)
            if role == "teacher":
                await message.answer(
                    "✅ Вы успешно зарегистрировались как учитель!"
                )
            elif role == "student":
                await message.answer(
                    "✅ Вы успешно зарегистрировались как ученик!"
                )

    await state.clear()  # Очищаем состояние


@router.callback_query(F.data == "add_lection")
async def add_material_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📘 Введите тему учебного материала:")
    await state.set_state(Capitals.add_material_theme)
    await callback.answer()


@router.message(Capitals.add_material_theme)
async def process_material_theme(message: Message, state: FSMContext):
    theme = message.text
    await state.update_data(theme=theme)  # Сохраняем тему в состояние
    await message.answer("📄 Введите текст учебного материала:")
    await state.set_state(Capitals.add_material_text)


@router.message(Capitals.add_material_text)
async def process_material_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(material=text)  # Сохраняем текст материала
    await message.answer("📎 Выберите тип контента:", reply_markup=await kb.choose_content_type())
    await state.set_state(Capitals.add_material_media)


@router.callback_query(F.data == "skip_media")
async def skip_media(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    theme = data.get("theme")
    material = data.get("material")

    # Сохраняем материал без медиа
    await set_material(
        theme=theme,
        material=material,
        image_url=None,
        video_url=None,
        audio_url=None,
        animation_url=None
    )

    # Отправляем сообщение об успешном добавлении материала с клавиатурой
    await callback.message.answer(
        "✅ Учебный материал успешно добавлен!",
        reply_markup=await kb.after_add()
    )

    # Очищаем состояние
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.in_(["add_image", "add_video", "add_audio", "add_animation"]))
async def process_content_choice(callback: CallbackQuery, state: FSMContext):
    content_type = callback.data.split("_")[1]

    await state.update_data(media_type=content_type)  # Сохраняем тип медиа

    media_prompts = {
        "image": "🖼️ Загрузите изображение:",
        "video": "🎥 Загрузите видео:",
        "audio": "🎵 Загрузите аудио:",
        "animation": "🎬 Загрузите анимацию:"
    }

    await callback.message.answer(media_prompts[content_type])
    await state.set_state(Capitals.add_material_media)

    await callback.answer()



@router.message(Capitals.add_material_media, F.photo | F.video | F.audio | F.animation)
async def process_media_upload(message: Message, state: FSMContext):
    data = await state.get_data()
    media_type = data.get("media_type")

    if media_type == "image" and message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(image_url=file_id)
    elif media_type == "video" and message.video:
        file_id = message.video.file_id
        await state.update_data(video_url=file_id)
    elif media_type == "audio" and message.audio:
        file_id = message.audio.file_id
        await state.update_data(audio_url=file_id)
    elif media_type == "animation" and message.animation:
        file_id = message.animation.file_id
        await state.update_data(animation_url=file_id)

    # Проверяем, что файл был загружен
    if not any([message.photo, message.video, message.audio, message.animation]):
        await message.answer("⚠️ Файл не был загружен. Пожалуйста, отправьте файл соответствующего типа.")
        return

    # Сохраняем материал
    await process_save_material(message, state)


async def process_save_material(message: Message, state: FSMContext):
    data = await state.get_data()
    theme = data.get("theme")
    material = data.get("material")
    image_url = data.get("image_url")
    video_url = data.get("video_url")
    audio_url = data.get("audio_url")
    animation_url = data.get("animation_url")

    # Сохраняем материал в базу данных
    await set_material(
        theme=theme,
        material=material,
        image_url=image_url,
        video_url=video_url,
        audio_url=audio_url,
        animation_url=animation_url
    )

    await message.answer(
        "✅ Учебный материал успешно добавлен!",
        reply_markup=await kb.after_add()
    )
    await state.clear()  # Очищаем состояние


@router.callback_query(F.data == "change_lection")
async def edit_material_start(callback: CallbackQuery, state: FSMContext):
    themes = await get_all_themes()

    if not themes:
        await callback.message.answer("🚫 Нет доступных материалов для редактирования.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📘 {theme}", callback_data=f"theme_{theme}")]
        for theme in themes
    ])

    await callback.message.answer("📎 Выберите тему материала:", reply_markup=keyboard)
    await state.set_state(Capitals.edit_material_select)
    await callback.answer()


@router.callback_query(Capitals.edit_material_select, F.data.startswith("theme_"))
async def select_theme(callback: CallbackQuery, state: FSMContext):
    theme = callback.data.split("_")[1]  # Выбранная тема
    materials = await get_materials_by_theme(theme)  # Получаем материалы по теме

    if not materials:
        await callback.message.answer("❌ Материалы для этой темы не найдены.")
        await callback.answer()
        return

    for material in materials:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Выбрать этот материал", callback_data=f"edit_{material.id}")]
        ])

        # Отправляем содержимое материала и уникальную клавиатуру для выбора
        await callback.message.answer(
            f"📘 Тема: {material.theme}\n\n📄 Текст: {material.material}",
            reply_markup=keyboard
        )

    await state.set_state(Capitals.edit_material_field)  # Переходим к выбору поля
    await callback.answer()


@router.callback_query(Capitals.edit_material_field, F.data.startswith("edit_"))
async def select_material_to_edit(callback: CallbackQuery, state: FSMContext):
    material_id = int(callback.data.split("_")[1])  # ID выбранного материала
    await state.update_data(material_id=material_id)

    await callback.message.answer(
        "🛠 Что вы хотите изменить?",
        reply_markup=await kb.choose_what_change()
    )

    await state.set_state(Capitals.edit_material_value)  # Переходим к выбору поля
    await callback.answer()

@router.callback_query(Capitals.edit_material_value, F.data.startswith("edit_"))
async def select_field_to_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[1]  # Поле для изменения (theme, material, image_url, и т.д.)
    await state.update_data(field=field)

    prompts = {
        "theme": "📘 Введите новую тему:",
        "material": "📄 Введите новый текст:"
    }

    if field not in prompts:
        await callback.message.answer("⚠️ Недопустимое поле для изменения.")
        await callback.answer()
        return

    await callback.message.answer(prompts[field])
    await state.set_state(Capitals.edit_material_value2)
    await callback.answer()


@router.message(Capitals.edit_material_value2)
async def update_material_value(message: Message, state: FSMContext):
    data = await state.get_data()
    material_id = data.get("material_id")
    field = data.get("field")

    if field in ["theme", "material"]:
        new_value = message.text

    # Обновляем материал в базе данных
    await update_material(material_id, field, new_value)
    await message.answer(
        "✅ Материал успешно обновлен!",
        reply_markup=await kb.after_change()
    )
    await state.clear()


@router.callback_query(F.data == "add_test")
async def add_test_from_text_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🧪 Введите название теста:")
    await state.set_state(Capitals.add_test_name)
    await callback.answer()


@router.message(Capitals.add_test_name)
async def process_test_name(message: Message, state: FSMContext):
    test_name = message.text.strip()

    if not test_name:
        await message.answer("⚠️ Название теста не может быть пустым. Попробуйте снова.")
        return

    # Сохраняем название теста в состояние
    await state.update_data(test_name=test_name)

    await message.answer(
        "✍️ Введите тест в следующем формате:\n"
        "тип вопроса(1 - текст, 2 - множественный выбор, 3 - соответствие), вопрос | ответ\n"
        "\nПример:\n"
        "1, Какой столицей является Москва? | Россия\n"
        "2, Выберите все страны Европы | Германия, Франция, Италия\n"
        "3, Соотнесите столицы и страны | Россия-Москва, Франция-Париж"
    )
    await state.set_state(Capitals.add_test_from_text)


@router.message(Capitals.add_test_from_text)
async def process_test_from_text(message: Message, state: FSMContext):
    raw_text = message.text.strip()

    # Разбиваем текст на строки по символу новой строки
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    if not lines:
        await message.answer("⚠️ Тест не содержит вопросов. Попробуйте снова.")
        return

    # Получаем название теста из состояния
    data = await state.get_data()
    test_name = data.get("test_name")

    # Переменная для хранения ID теста
    test_id = None

    for line in lines:
        try:
            # Разбираем строку на части
            question_type, rest = line.split(",", 1)
            question_type = int(question_type.strip())
            question_text, answer = rest.split("|", 1)
            question_text = question_text.strip()
            answer = answer.strip()

            # Определяем тип вопроса
            if question_type == 1:  # Текстовый вопрос
                question_type_str = "text"
                correct_answer = answer

            elif question_type == 2:  # Множественный выбор
                question_type_str = "multiple"
                options = [option.strip() for option in answer.split(",")]
                correct_answer = options[0]  # Первый вариант считается правильным

            elif question_type == 3:  # Вопрос на соответствие
                question_type_str = "matching"
                pairs = {}
                for pair in answer.split(","):
                    key, value = pair.split("-")
                    pairs[key.strip()] = value.strip()
                correct_answer = str(pairs)  # Сериализуем словарь в строку

            else:
                await message.answer(f"⚠️ Неверный тип вопроса: {question_type}. Пропускаю строку.")
                continue

            # Создаем тест, если он еще не создан
            if test_id is None:
                test_id = await create_test(test_name, async_session)  # Передаем название теста

            # Сохраняем вопрос в базу данных
            await save_question(
                test_id=test_id,
                question_text=question_text,
                question_type=question_type_str,
                options=options if question_type == 2 else None,
                pairs=pairs if question_type == 3 else None,
                correct_answer=correct_answer,
                async_session=async_session  # Передаем async_session
            )

        except Exception as e:
            print(f"Ошибка при обработке строки '{line}': {e}")
            await message.answer(f"⚠️ Ошибка при обработке строки: '{line}'. Пропускаю её.")

    await message.answer(
        f"✅ Тест '{test_name}' успешно добавлен!",
        reply_markup=await kb.after_add_test()
    )
    await state.clear()


@router.callback_query(F.data == "edit_test")
async def edit_test_start(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        tests = await session.execute(select(Test))
        tests = tests.scalars().all()

    if not tests:
        await callback.message.answer("🚫 Нет доступных тестов для редактирования.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🧪 {test.name}", callback_data=f"edit_test_{test.id}")]
        for test in tests
    ])

    await callback.message.answer("📎 Выберите тест для редактирования:", reply_markup=keyboard)
    await state.set_state(Capitals.edit_test_select)
    await callback.answer()


@router.callback_query(Capitals.edit_test_select, F.data.startswith("edit_test_"))
async def select_test_to_edit(callback: CallbackQuery, state: FSMContext):
    test_id = int(callback.data.split("_")[2])  # ID выбранного теста
    await state.update_data(test_id=test_id)

    async with async_session() as session:
        questions = await session.execute(
            select(Question).where(Question.test_id == test_id)
        )
        questions = questions.scalars().all()

    if not questions:
        await callback.message.answer("❌ В этом тесте нет вопросов.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❓ {question.question_text[:20]}...", callback_data=f"edit_question_{question.id}")]
        for question in questions
    ])

    await callback.message.answer("📎 Выберите вопрос для редактирования:", reply_markup=keyboard)
    await state.set_state(Capitals.edit_question_select)
    await callback.answer()

@router.callback_query(Capitals.edit_question_select, F.data.startswith("edit_question_"))
async def select_question_to_edit(callback: CallbackQuery, state: FSMContext):
    question_id = int(callback.data.split("_")[2])  # ID выбранного вопроса
    await state.update_data(question_id=question_id)

    await callback.message.answer(
        "🛠 Что вы хотите изменить?",
        reply_markup=await kb.choose_what_change_test()
    )

    await state.set_state(Capitals.edit_question_field)
    await callback.answer()


@router.callback_query(Capitals.edit_question_field, F.data == "edit_field_name")
async def edit_question_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🖋 Введите новый текст вопроса:")
    await state.set_state(Capitals.edit_question_value)
    await state.update_data(field="name")
    await callback.answer()


@router.message(Capitals.edit_question_value)
async def update_question_value(message: Message, state: FSMContext):
    new_value = message.text
    data = await state.get_data()
    field = data.get("field")
    question_id = data.get("question_id")

    async with async_session() as session:
        question = await session.get(Question, question_id)
        if question:
            setattr(question, field, new_value)
            await session.commit()

    await message.answer(
        f"✅ Поле '{field}' успешно обновлено!",
        reply_markup=await kb.after_change_test()
    )
    await state.clear()


@router.callback_query(Capitals.edit_question_field, F.data == "delete_question")
async def delete_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_id = data.get("question_id")

    async with async_session() as session:
        # Удаляем связанные ответы
        await session.execute(
            delete(Answer).where(Answer.question_id == question_id)
        )

        # Удаляем сам вопрос
        question = await session.get(Question, question_id)
        if question:
            await session.delete(question)
            await session.commit()

    await callback.message.answer(
        "🗑 Вопрос успешно удален!",
        reply_markup=await kb.after_change_test()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(Capitals.edit_question_field, F.data == "edit_field_answers")
async def edit_question_answers(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_id = data.get("question_id")

    async with async_session() as session:
        answers = await session.execute(
            select(Answer).where(Answer.question_id == question_id)
        )
        answers = answers.scalars().all()

    if not answers:
        await callback.message.answer("🚫 У этого вопроса нет ответов.")
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔹 {answer.text[:30]}...", callback_data=f"edit_answer_{answer.id}")]
        for answer in answers
    ])

    await callback.message.answer("📎 Выберите ответ для редактирования:", reply_markup=keyboard)
    await state.set_state(Capitals.edit_answer_select)
    await callback.answer()


@router.callback_query(Capitals.edit_answer_select, F.data.startswith("edit_answer_"))
async def edit_answer_text(callback: CallbackQuery, state: FSMContext):
    answer_id = int(callback.data.split("_")[2])  # ID выбранного ответа
    await state.update_data(answer_id=answer_id)

    await callback.message.answer("📝 Введите новый текст ответа:")
    await state.set_state(Capitals.edit_answer_value)
    await callback.answer()


@router.message(Capitals.edit_answer_value)
async def update_answer_text(message: Message, state: FSMContext):
    new_answer_text = message.text
    data = await state.get_data()
    answer_id = data.get("answer_id")

    async with async_session() as session:
        answer = await session.get(Answer, answer_id)
        if answer:
            answer.text = new_answer_text
            await session.commit()

    await message.answer(
        "✅ Текст ответа успешно обновлен!",
        reply_markup=await kb.after_change_test()
    )
    
    await state.clear()


@router.callback_query(F.data == "learn_lection")
async def show_materials_for_student(callback: CallbackQuery):
    async with async_session() as session:
        # Получаем только видимые материалы
        themes = await session.execute(
            select(distinct(Material.theme)).where(Material.is_hidden == False)
        )
        themes = [row[0] for row in themes.fetchall()]

    if not themes:
        await callback.message.answer("🚫 Нет доступных учебных материалов.")
        await callback.answer()
        return

    # Создаем клавиатуру с темами
    keyboard = InlineKeyboardBuilder()
    for theme in themes:
        keyboard.add(InlineKeyboardButton(text=f"📘 {theme}", callback_data=f"material_theme_{theme}"))

    await callback.message.answer(
        "🎓 Выберите тему для изучения:",
        reply_markup=keyboard.adjust(1).as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("material_theme_"))
async def show_material_by_theme(callback: CallbackQuery):
    theme = callback.data.split("_")[2]  # Извлекаем название темы

    async with async_session() as session:
        # Получаем материалы для выбранной темы
        materials = await session.execute(
            select(Material).where(Material.theme == theme)
        )
        materials = materials.scalars().all()

    if not materials:
        await callback.message.answer(f"🚫 Нет материалов для темы '{theme}'.")
        await callback.answer()
        return

    # Отправляем каждый материал пользователю
    for material in materials:
        message_text = f"📘 Тема: {material.theme}\n\n"
        message_text += f"📄 Материал:\n{material.material}\n\n"

        # Добавляем медиафайлы, если они есть
        if material.image_url:
            await callback.message.answer_photo(material.image_url)
        if material.video_url:
            await callback.message.answer_video(material.video_url)
        if material.audio_url:
            await callback.message.answer_audio(material.audio_url)
        if material.animation_url:
            await callback.message.answer_animation(material.animation_url)

        await callback.message.answer(message_text)
        await callback.message.answer(
            "📎 Выберите следующее действие",
            reply_markup=await kb.after_learn_lection()
        )

    await callback.answer()


@router.callback_query(F.data == "have_test")
async def show_tests(callback: CallbackQuery):
    async with async_session() as session:
        # Получаем все доступные тесты
        tests = await session.execute(select(Test))
        tests = tests.scalars().all()

    if not tests:
        await callback.message.answer("🚫 Нет доступных тестов.")
        await callback.answer()
        return

    # Создаем клавиатуру с тестами
    keyboard = InlineKeyboardBuilder()
    for test in tests:
        keyboard.add(InlineKeyboardButton(text=f"🧪 {test.name}", callback_data=f"start_test_{test.id}"))

    await callback.message.answer(
        "🧠 Выберите тест для прохождения:",
        reply_markup=keyboard.adjust(1).as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("start_test_"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    test_id = int(callback.data.split("_")[2])  # ID выбранного теста
    await state.update_data(test_id=test_id, current_question_index=0, score=0)

    async with async_session() as session:
        # Получаем все вопросы для выбранного теста
        questions = await session.execute(
            select(Question).where(Question.test_id == test_id)
        )
        questions = questions.scalars().all()

    if not questions:
        await callback.message.answer("❌ В этом тесте нет вопросов.")
        await callback.answer()
        return

    await state.update_data(questions=[q.id for q in questions])  # Сохраняем ID вопросов
    await show_next_question(callback.message, state)
    await callback.answer()


async def show_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions")
    current_question_index = data.get("current_question_index")

    if current_question_index >= len(questions):
        # Если вопросы закончились, завершаем тест
        await finish_test(message, state)
        return

    question_id = questions[current_question_index]
    async with async_session() as session:
        # Получаем текущий вопрос
        question = await session.get(Question, question_id)
        answers = await session.execute(
            select(Answer).where(Answer.question_id == question_id)
        )
        answers = answers.scalars().all()

    # Формируем текст вопроса
    question_text = f"❓ Вопрос: {question.name}\n\n"

    if question.type == 1:  # Текстовый ответ
        question_text += "✍️ Введите ваш ответ:"
        await message.answer(question_text)
        await state.set_state(Capitals.answer_text_question)
    elif question.type == 2:  # Множественный выбор
        keyboard = InlineKeyboardBuilder()
        for answer in answers:
            keyboard.add(InlineKeyboardButton(text=f"🔹 {answer.text}", callback_data=f"answer_{answer.id}"))
        await message.answer(question_text, reply_markup=keyboard.adjust(1).as_markup())
        await state.set_state(Capitals.answer_multiple_choice_question)
    elif question.type == 3:  # На соответствие
        pairs = {answer.pair_key: answer.pair_value for answer in answers}
        question_text += "🔗 Установите соответствие, введите ответ без пробелов(вопрос1-ответ1,вопрос2-ответ2):\n"
        for key in pairs.keys():
            question_text += f"{key}\n"
        await message.answer(question_text)
        await state.set_state(Capitals.answer_matching_question)


@router.message(Capitals.answer_text_question)
async def process_text_answer(message: Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    questions = data.get("questions")
    current_question_index = data.get("current_question_index")

    async with async_session() as session:
        question_id = questions[current_question_index]
        correct_answer = await session.execute(
            select(Answer.text).where(Answer.question_id == question_id, Answer.is_correct == True)
        )
        correct_answer = correct_answer.scalar()

    # Проверяем ответ
    if user_answer.strip().lower() == correct_answer.strip().lower():
        await message.answer("✅ Правильно!")
        await state.update_data(score=data.get("score", 0) + 1)
    else:
        await message.answer(f"❌ Неправильно. Правильный ответ: {correct_answer}")

    # Переходим к следующему вопросу
    await state.update_data(current_question_index=current_question_index + 1)
    await show_next_question(message, state)


@router.callback_query(Capitals.answer_multiple_choice_question, F.data.startswith("answer_"))
async def process_multiple_choice_answer(callback: CallbackQuery, state: FSMContext):
    answer_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    questions = data.get("questions")
    current_question_index = data.get("current_question_index")

    async with async_session() as session:
        question_id = questions[current_question_index]
        correct_answer = await session.execute(
            select(Answer.is_correct).where(Answer.id == answer_id)
        )
        is_correct = correct_answer.scalar()

    # Проверяем ответ
    if is_correct:
        await callback.message.answer("✅ Правильно!")
        await state.update_data(score=data.get("score", 0) + 1)
    else:
        await callback.message.answer("❌ Неправильно.")

    # Переходим к следующему вопросу
    await state.update_data(current_question_index=current_question_index + 1)
    await show_next_question(callback.message, state)
    await callback.answer()


@router.message(Capitals.answer_matching_question)
async def process_matching_answer(message: Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    questions = data.get("questions")
    current_question_index = data.get("current_question_index")

    async with async_session() as session:
        question_id = questions[current_question_index]
        correct_pairs = await session.execute(
            select(Answer.pair_key, Answer.pair_value).where(Answer.question_id == question_id)
        )
        correct_pairs = {key: value for key, value in correct_pairs.fetchall()}

    # Проверяем ответ
    try:
        user_pairs = dict(pair.split("-") for pair in user_answer.split(","))
        if user_pairs == correct_pairs:
            await message.answer("✅ Правильно!")
            await state.update_data(score=data.get("score", 0) + 1)
        else:
            await message.answer(f"❌ Неправильно. Правильный ответ: {correct_pairs}")
    except ValueError:
        await message.answer("⚠️ Неверный формат ответа. Используйте формат 'ключ-значение' через запятую.")

    # Переходим к следующему вопросу
    await state.update_data(current_question_index=current_question_index + 1)
    await show_next_question(message, state)

async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0)
    total_questions = len(data.get("questions", []))
    test_id = data.get("test_id")
    current_id = await get_current_user(async_session)

    if not current_id:
        await message.answer("❌ Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы сохранить результаты.")
        await state.clear()
        return

    # Сохраняем результаты в базу данных
    await save_test_result(user_id=current_id, test_id=test_id, score=(score / total_questions * 100), async_session=async_session)

    # Отправляем сообщение с результатами
    await message.answer(
        f"🎉 Тест завершен!\n\n"
        f"✅ Правильных ответов: {score}/{total_questions}\n"
        f"📊 Процент выполнения: {int(score / total_questions * 100)}%",
        reply_markup=await kb.after_do_test()
    )

    await state.clear()


@router.callback_query(F.data == "hide_materials")
async def show_materials_to_hide(callback: CallbackQuery):
    async with async_session() as session:
        # Получаем все материалы
        materials = await session.execute(select(Material))
        materials = materials.scalars().all()

    if not materials:
        await callback.message.answer("🚫 Нет доступных материалов.")
        await callback.answer()
        return

    # Создаем клавиатуру с материалами
    keyboard = InlineKeyboardBuilder()
    for material in materials:
        status = "✅ Видимый" if not material.is_hidden else "❌ Скрытый"
        keyboard.add(
            InlineKeyboardButton(
                text=f"{material.theme} ({status})",
                callback_data=f"hide_material_{material.id}"
            )
        )
    # Отправляем сообщение с клавиатурой
    await callback.message.edit_text(
        "📎 Выберите материал для скрытия или отображения:",
        reply_markup=keyboard.adjust(1).as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hide_material_"))
async def toggle_material_visibility(callback: CallbackQuery):
    material_id = int(callback.data.split("_")[2])  # ID выбранного материала

    async with async_session() as session:
        material = await session.get(Material, material_id)
        if not material:
            await callback.answer("⚠️ Материал не найден.", show_alert=True)
            return

        # Переключаем статус видимости
        material.is_hidden = not material.is_hidden
        await session.commit()

    # Обновляем клавиатуру
    async with async_session() as session:
        materials = await session.execute(select(Material))
        materials = materials.scalars().all()

    if not materials:
        await callback.message.edit_text("🚫 Нет доступных материалов.")
        return

    # Создаем обновленную клавиатуру
    keyboard = InlineKeyboardBuilder()
    for material in materials:
        status = "✅ Видимый" if not material.is_hidden else "❌ Скрытый"
        keyboard.add(
            InlineKeyboardButton(
                text=f"{material.theme} ({status})",
                callback_data=f"hide_material_{material.id}"
            )
        )
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_t"))

    # Обновляем текущее сообщение
    await callback.message.edit_text(
        "📎 Выберите материал для скрытия или отображения:",
        reply_markup=keyboard.adjust(1).as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "results")
async def view_student_results_start(callback: CallbackQuery, state: FSMContext):
    # Получаем все доступные тесты
    tests = await get_all_tests(async_session)

    if not tests:
        await callback.message.answer("🚫 Нет доступных тестов.")
        await callback.answer()
        return

    # Создаем клавиатуру с тестами
    keyboard = InlineKeyboardBuilder()
    for test in tests:
        keyboard.add(
            InlineKeyboardButton(
                text=f"🧪 {test.name}",
                callback_data=f"view_results_test_{test.id}"
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="📊 Показать все результаты",
            callback_data="view_results_all"
        )
    )

    await callback.message.answer(
        "📈 Выберите тест, чтобы посмотреть результаты учеников, или нажмите 'Показать все результаты':",
        reply_markup=keyboard.adjust(1).as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_results_test_"))
async def view_results_for_test(callback: CallbackQuery):
    try:
        test_id = int(callback.data.split("_")[3])  # Извлекаем ID теста
    except (ValueError, IndexError):
        await callback.message.answer("⚠️ Произошла ошибка при выборе теста.")
        await callback.answer()
        return

    # Получаем результаты для выбранного теста
    results = await get_test_results(test_id, async_session)

    if not results:
        await callback.message.answer("🚫 Нет результатов для этого теста.")
        await callback.answer()
        return

    # Формируем сообщение с результатами
    message_text = f"📊 Результаты теста (ID: {test_id}):\n\n"
    for result in results:
        user_name = result.user.name if result.user else "👤 Неизвестный пользователь"
        message_text += (
            f"🎓 Студент: {user_name}\n"
            f"📅 Дата: {result.test_date}\n"
            f"💯 Оценка: {result.score}%\n"
            f"{'-' * 20}\n"
        )

    await callback.message.answer(message_text)
    await callback.message.answer(
        "📎 Выберите следующее действие",
        reply_markup=await kb.after_results()
    )
    await callback.answer()


@router.callback_query(F.data == "view_results_all")
async def view_all_results(callback: CallbackQuery):
    # Получаем все результаты
    results = await get_all_results(async_session)

    if not results:
        await callback.message.answer("🚫 Нет доступных результатов.")
        await callback.answer()
        return

    # Группируем результаты по тестам
    grouped_results = {}
    for result in results:
        test_name = result.test.name if result.test else "🧪 Неизвестный тест"
        if test_name not in grouped_results:
            grouped_results[test_name] = []
        grouped_results[test_name].append(result)

    # Формируем сообщение с результатами
    message_text = "📊 Все результаты:\n\n"
    for test_name, test_results in grouped_results.items():
        message_text += f"🧪 Тест: {test_name}\n"
        for result in test_results:
            user_name = result.user.name if result.user else "👤 Неизвестный пользователь"
            message_text += (
                f"🎓 Студент: {user_name}\n"
                f"📅 Дата: {result.test_date}\n"
                f"💯 Оценка: {result.score}%\n"
                f"{'-' * 20}\n"
            )
        message_text += "\n"

    await callback.message.answer(message_text)
    await callback.message.answer(
        "📎 Выберите следующее действие",
        reply_markup=await kb.after_results()
    )
    await callback.answer()