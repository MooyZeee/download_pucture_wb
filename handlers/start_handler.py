from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
from keyboard.keyboard import *
from auxiliary_functions.helper_func import *

router = Router()


class Reg(StatesGroup):
    id = State()
    remove_admin = State()
    download_picture = State()
    add_new_group_name = State()
    add_new_group_username = State()
    delete_group = State()
    get_player_id = State()
    download_video = State()


async def handle_subscription_check(message: Message, groups, keyboard_main_admin, keyboard_main):
    keyboard = []
    not_subscribed_channels = []

    list_admins = checked_admin_list()
    if message.from_user.id in list_admins:
        await message.answer('Выберите функцию', reply_markup=keyboard_main_admin)
        return

    for i in groups:
        member = await message.bot.get_chat_member(chat_id=f'@{i["username"]}', user_id=message.from_user.id)
        if member.status not in ['member', 'creator', 'administrator']:
            keyboard.append([InlineKeyboardButton(text=f'{i["name"]}', url=f'https://t.me/{i["username"]}')])
            not_subscribed_channels.append(i)  # Добавляем неподписанный канал в список

    # Добавляем кнопку проверки подписок только если есть неподписанные каналы
    if not_subscribed_channels:
        keyboard.append([InlineKeyboardButton(text='Проверить подписку', callback_data='check_subscribes')])

    keyboard_subscribe = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if keyboard:  # Если есть каналы для подписки
        await message.answer('Подпишитесь на все каналы, чтобы продолжить пользоваться ботом!', reply_markup=keyboard_subscribe)
    else:
        await message.answer('Выберите функцию', reply_markup=keyboard_main)



@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    groups = load_from_json()
    a = get_anonim(message.from_user.id)

    if not a:
        print(111111)
        write_user_id(message.from_user.id, message.from_user.username, message.from_user.last_name)
        await handle_subscription_check(message, groups, keyboard_main_admin, keyboard_main)

    else:
        print(222222)
        await handle_subscription_check(message, groups, keyboard_main_admin, keyboard_main)


@router.callback_query(F.data == 'check_subscribes')
async def check_subscribes(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    not_subscribed_channels = []
    groups = load_from_json()
    try:
        for i in groups:
            member = await callback_query.bot.get_chat_member(chat_id=f'@{i["username"]}', user_id=user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                not_subscribed_channels.append(i["username"])

        if not_subscribed_channels:
            # Если есть неподписанные каналы, отправляем сообщение
            keyboard = [[InlineKeyboardButton(text=f'{channel}', url=f'https://t.me/{channel}') for channel in not_subscribed_channels]]
            keyboard.append([InlineKeyboardButton(text='Проверить подписку', callback_data='check_subscribes')])
            keyboard_subscribe = InlineKeyboardMarkup(inline_keyboard=keyboard)

            await callback_query.message.answer('Вы не подписаны на следующие каналы ;', reply_markup=keyboard_subscribe)
        else:
            await callback_query.message.answer('Выберите функцию', reply_markup=keyboard_main)

    except Exception as e:
        print(f"Error checking subscriptions: {e}")
        await callback_query.answer("Произошла ошибка при проверке подписок.")


@router.callback_query(F.data == 'download_picture_data')
async def download_picture_func(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отправьте ссылку или артикул товара')
    await state.set_state(Reg.download_picture)


@router.message(Reg.download_picture)
async def download_picture_func_fsm(message: Message, state: FSMContext):
    waiting_message = await message.answer('Ожидайте! Ваш запрос выполняется...')
    url = message.text
    # Получаем информацию о продукте
    result = get_product_info(url)

    # Проверяем, вернула ли функция корректные данные
    if not result:
        await waiting_message.delete()
        await message.answer('Не удалось получить информацию о товаре. Необходимо отправить ссылку без текстового описания.')
        return

    # Распаковка данных
    name_product, old_price, new_price, brand, item_goods, rating_goods, url_photo, feedbacks, desc = result

    await state.update_data(download_picture_func=url)
    url_photo_split = [i for i in url_photo.split('\n') if i]  # Убираем пустые строки
    media = []

    try:
        await asyncio.sleep(5)
        await waiting_message.delete()

        for i in url_photo_split:
            media.append(InputMediaPhoto(media=i, caption=f'Готово! ✅\n\n'
                                                          f'<b>Название товара:</b> <i>{name_product}</i>\n'
                                                          f'<b>Артикул товара:</b> <i>{item_goods}</i>\n'
                                                          f'<b>Цена со скидкой:</b> <i>{int(new_price)} ₽</i>\n'
                                                          f'<b>Цена без скидки:</b> <i>{int(old_price)} ₽</i>\n'
                                                          f'<b>Рейтинг товара:</b> <i>{rating_goods}</i>\n'
                                                          f'<b>Название бренда:</b> <i>{brand}</i>\n'
                                                          f'<b>Ссылка на товар:</b> <i>{message.text}</i>\n'
                                                          f'<b>Отзывы:</b> <i>{feedbacks}</i>'))

        await message.bot.send_media_group(chat_id=message.from_user.id, media=media)
        await message.bot.send_message(chat_id=message.from_user.id, text=f'Готово! ✅\n\n'
                                                                          f'<b>Название товара:</b> <i>{name_product}</i>\n'
                                                                          f'<b>Артикул товара:</b> <i>{item_goods}</i>\n'
                                                                          f'<b>Цена со скидкой:</b> <i>{int(new_price)} ₽</i>\n'
                                                                          f'<b>Цена без скидки:</b> <i>{int(old_price)} ₽</i>\n'
                                                                          f'<b>Рейтинг товара:</b> <i>{rating_goods}</i>\n'
                                                                          f'<b>Название бренда:</b> <i>{brand}</i>\n'
                                                                          f'<b>Ссылка на товар:</b> <i>{message.text}</i>\n'
                                                                          f'<b>Отзывы:</b> <i>{feedbacks}</i>\n\n'
                                                                          f'<b>Описание:</b> <i>{desc}</i>',
                                       reply_markup=more_keyboard, disable_web_page_preview=True)
        await state.clear()

    except Exception as e:
        await message.answer(f'Ошибка: {e}! Проверьте валидность ссылки или что-то!')


@router.callback_query(F.data == 'more_download_picture')
async def more_download(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.download_picture)
    await callback.answer('More downloading :///')
    await callback.message.answer('Продолжим скачивание! Отправьте ссылку или артикул товара.')


@router.callback_query(F.data == 'more_stop')
async def more_send_stop(callback: CallbackQuery):
    list_admins = checked_admin_list()
    if callback.from_user.id in list_admins:
        await callback.message.answer('Выберите функцию', reply_markup=keyboard_main_admin)
    else:
        await callback.message.answer('Выберите функцию', reply_markup=keyboard_main)


@router.callback_query(F.data == 'download_video_data')
async def send_download_video_data(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отправьте ссылку или артикул товара')
    await state.set_state(Reg.download_video)

@router.message(Reg.download_video)
async def fsm_send_download_video(message: Message, state: FSMContext):
    message_sabr = await message.answer('Ожидайте! Скачивание выполняется..')
    message_url_or_feedback = message.text

    func_return_url_video = construct_host_v2(message_url_or_feedback, "video")

    if not func_return_url_video:
        await message_sabr.delete()
        await message.answer('Ошибка: Неверный ID или тип видео.', reply_markup=more_keyboard_video)
        return

    try:
        response = requests.head(func_return_url_video)  # Используем HEAD-запрос для проверки доступности
        response.raise_for_status()  # Вызывает исключение для статусов 4xx и 5xx

        await message_sabr.delete()
        await message.bot.send_video(message.chat.id, video=func_return_url_video, caption='✅ Готово', reply_markup=more_keyboard_video)
        await state.clear()

    except requests.HTTPError:
        await message_sabr.delete()
        await message.answer('Произошла ошибка! Возможно на товаре отсутствует видео или неверная ссылка.', reply_markup=more_keyboard_video)
    except requests.RequestException as req_err:
        await message_sabr.delete()
        await message.answer(f'Сетевая ошибка: {req_err}')
    except Exception as e:
        await message_sabr.delete()
        await message.answer(f'Неизвестная ошибка: {e}')


@router.callback_query(F.data == 'more_download_video')
async def more_download(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.download_video)
    await callback.answer('More downloading :///')
    await callback.message.answer('Продолжим! Отправьте ссылку или артикул товара.')



###
@router.callback_query(F.data == 'admin_data')
async def cmd_admin(callback: CallbackQuery):
    await callback.message.answer('Выберите действие', reply_markup=add_new_admin_user_keyboard)


@router.callback_query(F.data == 'new_admin_data')
async def new_admin_user_func(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите ID пользователя, которого хотите добавить как админ',
                                     reply_markup=back_keyboard)
    await state.set_state(Reg.id)


@router.message(Reg.id)
async def add_admin_id(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    try:
        a = add_new_admin_db(message.text)

        # Добавляем ID пользователя в список администраторов
        if a:
            print('Администратор был успешно добавлен в базу данных')
            await message.answer(f'Пользователь с ID {message.text} добавлен как админ.', reply_markup=back_keyboard)
            await state.clear()

        else:
            await message.answer('Не удалось найти пользователя по этому ID или уже существует такой Администратор!')
            print('Не удалось найти пользователя по данному ID')

    except ValueError as e:
        await message.answer(f'Ошибка добавления пользователя. Ошибка: {e}')


@router.callback_query(F.data == 'remove_admin_list_data')
async def remove_admin_func(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите ID пользователь, которого хотите удалить', reply_markup=back_keyboard)
    await state.set_state(Reg.remove_admin)


@router.message(Reg.remove_admin)
async def remove_admin(message: Message, state: FSMContext):
    try:
        if remove_admin_from_db(message.text):
            print("Администратор успешно удален из базы данных.")
            await message.answer(f'Пользователь с ID {message.text} был удален!', reply_markup=back_keyboard)
            await state.clear()
        else:
            print("Не удалось найти администратора в базе данных.")
            await message.answer('Не удалось найти администратора в базе данных.')

    except ValueError as e:
        await message.answer(f'Ошибка удаления пользователя. Ошибка: {e}')


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
        await message.answer(f'Ошибка! Группа с таким username уже существует: {group_data["username"]}', reply_markup=back_keyboard)
        await state.clear()
        return False

    await message.answer(f'Отлично! Информацию про новую группу:\nUsername: {group_data["username"]}\nName: {group_data["name"]}', reply_markup=back_keyboard)
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
            await message.answer(f'Группа с Username: {message_text} успешно удалена!')
            await state.clear()

        else:
            await message.answer('Ошибка! Невозможно найти группу с таким Username!')

    except KeyError as e:
        await message.answer(f'Ошибка типа 3453-234567 - {e}!')


@router.callback_query(F.data == 'list_group_data')
async def group_list_db(callback: CallbackQuery):
    groups = load_from_json()

    if not groups:
        await callback.message.answer("Нет добавленных групп.")
        return

    keyboard = []

    for group in groups:
        keyboard.append([InlineKeyboardButton(text=f'{group["name"]}', url=f'https://t.me/{group["username"]}')])

    keyboard_list = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer('Список всех групп', reply_markup=keyboard_list)


@router.callback_query(F.data == 'back_data2')
async def back_func_2(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите действие', show_alert=True, reply_markup=add_new_admin_user_keyboard)
    await state.clear()
###
