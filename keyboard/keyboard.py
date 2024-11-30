from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


keyboard_main_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Получить информацию о товаре', callback_data='download_picture_data')],
    [InlineKeyboardButton(text='Скачать видео с товара', callback_data='download_video_data')],
    [InlineKeyboardButton(text='Админ панель', callback_data='admin_data')],
])

keyboard_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Получить информацию о товаре', callback_data='download_picture_data')],
    [InlineKeyboardButton(text='Скачать видео с товара', callback_data='download_video_data')]
])

add_new_admin_user_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧑‍💼Рассылка', callback_data='broadcast_message')],
    [InlineKeyboardButton(text='🧑‍💼Добавить нового админа', callback_data='new_admin_data')],
    [InlineKeyboardButton(text='❌Удалить админа', callback_data='remove_admin_list_data')],
    [InlineKeyboardButton(text='📈Добавить новую группу для подписки', callback_data='add_new_group_username_data')],
    [InlineKeyboardButton(text='📉Удалить группу', callback_data='delete_group_data')],
    [InlineKeyboardButton(text='📁Список групп', callback_data='list_group_data')],
    [InlineKeyboardButton(text='🧑Cписок администрации', callback_data='database_list_admin_data')],
    [InlineKeyboardButton(text='🧑‍💼Получить ID пользователя', callback_data='get_player_id')],
    [InlineKeyboardButton(text='🔙Назад', callback_data='back_data')]
])


back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙Назад', callback_data='back_data2')]
])


more_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Другой товар', callback_data='more_download_picture')],
    [InlineKeyboardButton(text='🔙Назад', callback_data='more_stop')],
])

more_keyboard_video = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Другой товар', callback_data='more_download_video')],
    [InlineKeyboardButton(text='🔙Назад', callback_data='more_stop')],
])






