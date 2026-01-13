from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


login = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 Войти или зарегистрироваться")]
    ],
    resize_keyboard=True
)


logout = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚪 Выйти из аккаунта")]
    ],
    resize_keyboard=True
)

async def choose_choice():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔓 Войти", callback_data="sign_in"))
    keyboard.add(InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="sign_up"))
    return keyboard.adjust(1).as_markup()


async def choose_status():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🧑‍🏫 Учитель", callback_data="teacher"))
    keyboard.add(InlineKeyboardButton(text="🎓 Ученик", callback_data="student"))
    return keyboard.adjust(1).as_markup()


async def choose_teacher_action():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📘 Добавить учебный материал", callback_data="add_lection"))
    keyboard.add(InlineKeyboardButton(text="✏️ Изменить учебный материал", callback_data="change_lection"))
    keyboard.add(InlineKeyboardButton(text="👁 Скрыть учебные материалы", callback_data="hide_materials"))
    keyboard.add(InlineKeyboardButton(text="🧪 Добавить тест", callback_data="add_test"))
    keyboard.add(InlineKeyboardButton(text="📈 Узнать результаты учеников", callback_data="results"))
    return keyboard.adjust(1).as_markup()


async def choose_content_type():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🖼 Добавить изображение", callback_data="add_image"))
    keyboard.add(InlineKeyboardButton(text="🎥 Добавить видео", callback_data="add_video"))
    keyboard.add(InlineKeyboardButton(text="🎵 Добавить аудио", callback_data="add_audio"))
    keyboard.add(InlineKeyboardButton(text="🎬 Добавить анимацию", callback_data="add_animation"))
    keyboard.add(InlineKeyboardButton(text="📄 Продолжить без медиа", callback_data="skip_media"))
    return keyboard.adjust(1).as_markup()


async def choose_what_change():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✏️ Изменить тему", callback_data="edit_theme"))
    keyboard.add(InlineKeyboardButton(text="🖋 Изменить текст", callback_data="edit_material"))
    return keyboard.adjust(1).as_markup()


async def after_add():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="➕ Добавить лекцию", callback_data="add_lection"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_t"))
    return keyboard.adjust(1).as_markup()


async def after_change():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔄 Изменить лекцию", callback_data="change_lection"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_t"))
    return keyboard.adjust(1).as_markup()


async def choose_question_type():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✍️ Текстовый ответ", callback_data="type_text"))
    keyboard.add(InlineKeyboardButton(text="🔹 Выбор из множества", callback_data="type_multiple"))
    keyboard.add(InlineKeyboardButton(text="🔗 На соответствие", callback_data="type_matching"))
    return keyboard.adjust(1).as_markup()


async def choose_what_change_test():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✏️ Изменить текст вопроса", callback_data="edit_field_name"))
    keyboard.add(InlineKeyboardButton(text="🔹 Изменить ответы", callback_data="edit_field_answers"))
    keyboard.add(InlineKeyboardButton(text="🗑 Удалить вопрос", callback_data="delete_question"))
    return keyboard.adjust(1).as_markup()


async def choose_student_action():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📘 Изучить учебный материал", callback_data="learn_lection"))
    keyboard.add(InlineKeyboardButton(text="🧠 Пройти тест", callback_data="have_test"))
    return keyboard.adjust(1).as_markup()


async def after_add_test():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="➕ Новый тест", callback_data="add_test"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_t"))
    return keyboard.adjust(1).as_markup()


async def after_change_test():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔄 Изменить тест", callback_data="edit_test"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_t"))
    return keyboard.adjust(1).as_markup()


async def after_learn_lection():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📘 Изучить учебный материал", callback_data="learn_lection"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_s"))
    return keyboard.adjust(1).as_markup()


async def after_do_test():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🧠 Пройти тест", callback_data="have_test"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_s"))
    return keyboard.adjust(1).as_markup()


async def after_results():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📊 Узнать результаты", callback_data="results"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu_t"))
    return keyboard.adjust(1).as_markup()