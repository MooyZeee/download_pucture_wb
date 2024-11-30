from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from help_functions.helper_func import *
from keyboard.keyboard import *
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

router = Router()


class Reg(StatesGroup):
    new_admin = State()
    remove_admin = State()
    add_new_group_name = State()
    add_new_group_username = State()
    delete_group = State()
    get_player_id = State()
    text = State()


@router.callback_query(F.data == 'admin_data')
async def cmd_admin(callback: CallbackQuery):
    await callback.message.answer('Выберите действие', reply_markup=add_new_admin_user_keyboard)


@router.callback_query(F.data == 'new_admin_data')
async def new_admin_user_func(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите ID пользователя, которого хотите добавить как админ',
                                     reply_markup=back_keyboard)
    await state.set_state(Reg.new_admin)


@router.message(Reg.new_admin)
async def add_admin_id(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    try:
        a = add_new_admin_db(message.text)

        # Добавляем ID пользователя в список администраторов
        if a:
            print('Администратор был успешно добавлен в базу данных')
            await message.answer(f'Пользователь с ID {message.text} добавлен как админ.', reply_markup=add_new_admin_user_keyboard)
            await state.clear()

        else:
            await message.answer('Не удалось найти пользователя по этому ID или уже существует такой Администратор!', reply_markup=add_new_admin_user_keyboard)
            # print('Не удалось найти пользователя по данному ID')

    except ValueError as e:
        await message.answer(f'Ошибка добавления пользователя. Ошибка: {e}', reply_markup=add_new_admin_user_keyboard)


@router.callback_query(F.data == 'remove_admin_list_data')
async def remove_admin_func(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите ID пользователь, которого хотите удалить', reply_markup=back_keyboard)
    await state.set_state(Reg.remove_admin)


@router.message(Reg.remove_admin)
async def remove_admin(message: Message, state: FSMContext):
    try:
        if remove_admin_from_db(message.text):
            # print("Администратор успешно удален из базы данных.")
            await message.answer(f'Пользователь с ID {message.text} был удален!', reply_markup=add_new_admin_user_keyboard)
            await state.clear()
        else:
            # print("Не удалось найти администратора в базе данных.")
            await message.answer('Не удалось найти администратора в базе данных.', reply_markup=add_new_admin_user_keyboard)

    except ValueError as e:
        await message.answer(f'Ошибка удаления пользователя. Ошибка: {e}', reply_markup=add_new_admin_user_keyboard)


@router.callback_query(F.data == 'add_new_group_username_data')
async def add_new_group_username_db(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Отправьте username канала/группы (без использования @)!',
                                     reply_markup=back_keyboard)
    await state.set_state(Reg.add_new_group_username)


@router.message(Reg.add_new_group_username)
async def fsm_add_new_group_username(message: Message, state: FSMContext):
    await message.answer(f'Хорошо! Username: {message.text}; Теперь отправьте название канала которое будет отображаться на кнопке!')
    await state.update_data(add_new_group_username=message.text)
    await state.set_state(Reg.add_new_group_name)


@router.message(Reg.add_new_group_name)
async def fsm_add_new_group_name(message: Message, state: FSMContext):
    await state.update_data(add_new_group_name=message.text)
    information_group = await state.get_data()

    # Сохраняем данные в JSON файл
    group_data = {
        'username': information_group['add_new_group_username'],
        'name': information_group['add_new_group_name']
    }
    if not writer_group_to_json(group_data):
        await message.answer(f'Ошибка! Группа с таким username уже существует: {group_data["username"]}', reply_markup=add_new_admin_user_keyboard)
        await state.clear()
        return False

    await message.answer(f'Отлично! Информацию про новую группу:\nUsername: {group_data["username"]}\nName: {group_data["name"]}', reply_markup=add_new_admin_user_keyboard)
    await state.clear()


@router.callback_query(F.data == 'delete_group_data')
async def remove_group_db_func(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Send username in the remove group/chanel (dont use "@")',
                                     reply_markup=back_keyboard)
    await state.set_state(Reg.delete_group)


@router.message(Reg.delete_group)
async def fsm_remove_group_db(message: Message, state: FSMContext):
    try:
        message_text = message.text
        remove_func = remove_group_from_json(message_text)
        if remove_func:
            await message.answer(f'Группа с Username: {message_text} успешно удалена!', reply_markup=add_new_admin_user_keyboard)
            await state.clear()

        else:
            await message.answer('Ошибка! Невозможно найти группу с таким Username!', reply_markup=add_new_admin_user_keyboard)

    except KeyError as e:
        await message.answer(f'Ошибка типа 3453-234567 - {e}!')


@router.callback_query(F.data == 'list_group_data')
async def group_list_db(callback: CallbackQuery):
    groups = load_from_json()

    if not groups:
        await callback.message.answer("Нет добавленных групп.", reply_markup=add_new_admin_user_keyboard)
        return

    keyboard = []

    for group in groups:
        keyboard.append([InlineKeyboardButton(text=f'{group["name"]}', url=f'https://t.me/{group["username"]}')])

    keyboard_list = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer('Список всех групп', reply_markup=keyboard_list)


@router.callback_query(F.data == 'back_data2')
async def back_func_2(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text('Выберите действие', show_alert=True, reply_markup=add_new_admin_user_keyboard)


Base = declarative_base()


# Модель пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, unique=True, nullable=False)


# Инициализация базы данных
DATABASE_URL = "sqlite:///bot.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


# Обработчик текстовых и медиа-сообщений в состоянии Letter.text
@router.message(Reg.text, F.content_type.in_({"text", "photo", "video", "document"}))
async def send_broadcast(message: Message, state: FSMContext):
    session = SessionLocal()
    users = session.query(User).all()

    success = 0
    failed = 0

    for user in users:
        try:
            # Определяем тип контента
            if message.text:
                # Рассылка текста
                await message.bot.send_message(chat_id=int(user.chat_id), text=message.text)
            elif message.photo:
                # Рассылка фото
                await message.bot.send_photo(
                    chat_id=int(user.chat_id),
                    photo=message.photo[-1].file_id,
                    caption=message.caption if message.caption else None
                )
            elif message.video:
                # Рассылка видео
                await message.bot.send_video(
                    chat_id=int(user.chat_id),
                    video=message.video.file_id,
                    caption=message.caption if message.caption else None
                )
            elif message.document:
                # Рассылка документа
                await message.bot.send_document(
                    chat_id=int(user.chat_id),
                    document=message.document.file_id,
                    caption=message.caption if message.caption else None
                )
            else:
                failed += 1
                continue

            success += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user.chat_id}: {e}")
            failed += 1

    # Отправляем итог админу
    await message.answer(f"Рассылка завершена.\nУспешно: {success}\nНеудачно: {failed}")

    # Завершаем состояние
    await state.clear()
    session.close()


# Обработчик нажатия кнопки "broadcast_message"
@router.callback_query(F.data == "broadcast_message")
async def handle_broadcast_button(callback_query: CallbackQuery, state: FSMContext):
    # Переход в состояние ввода текста или медиа для рассылки
    await callback_query.message.answer("Введите текст или отправьте медиа для рассылки:")
    await state.set_state(Reg.text)
    await callback_query.answer()
###
