import json
import re
import requests
import validators

admin_list = '../database/admin_list.txt'
player_data = '../database/players_list_db.txt'


def get_anonim(id):
    try:
        with open(f'{player_data}', 'r', encoding='utf-8') as file:
            # Читаем все строки и убираем пробелы
            data_id = {line.strip() for line in file if line.strip()}  # Используем множество
        return str(id) in data_id
    except FileNotFoundError:
        print(f"Файл {player_data} не найден.")
        return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False


def write_user_id(id_player, username, lastname):
    with open(f'{player_data}', 'a', encoding='utf-8') as file:
        file.write(f'\n{id_player}\n')
        file.write(f'Username: {username}, Lastname: {lastname}, ID: {id_player}')


def add_new_admin_db(add_admin_id):
    with open(f'{admin_list}', 'r', encoding='utf-8') as file:
        read_file = file.read()
        split_file = read_file.split('\n')
        if add_admin_id not in split_file:
            with open(f'{admin_list}', 'a', encoding='utf-8') as file2:
                file2.write(f'\n{add_admin_id}')
                return True

        elif add_admin_id in split_file:
            print('Такой пользователь уже существует!')
            return False

        else:
            # print('Возможно пользователь уже существует или введены не корректные данные.')
            print('Ошибка! 5534-235')
            return False


def remove_admin_from_db(admin_id):
    try:
        with open(f'{admin_list}', 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]

        if str(admin_id) in lines:
            lines.remove(str(admin_id))
            with open(f'{admin_list}', 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines))
            return True
        else:
            return False
    except FileNotFoundError:
        print(f"Файл '{admin_list}' не найден.")
        return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False


def checked_admin_list():
    with open(f'{admin_list}', 'r', encoding='utf-8') as file2:
        file_read = file2.readlines()
        file_split = [int(line.strip()) for line in file_read if line.strip()]

        return file_split


def get_product_info(url):
    try:
        item_id = int(__get_item_id(url))
        print(f"Извлеченный item_id: {item_id}")  # Выводим item_id для проверки
        response = requests.get(
            f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={item_id}")

        data = response.json()

        if "data" not in data or "products" not in data["data"] or not data["data"]["products"]:
            print("Нет данных о товаре.")

        product = data["data"]["products"][0]

        name = product.get("name")
        brand = product.get("brand")
        old_price = product.get("salePriceU") / 100
        discout = (3 / 100) * old_price
        price_with_discount = old_price - discout
        rating_goods = product.get('reviewRating')
        pics = product.get('pics')
        feedbacks = product.get('feedbacks')
        print(pics)

        for product in range(pics):
            _short_id = item_id // 100000
            """Используем match/case для определения basket на основе _short_id"""
            if 0 <= _short_id <= 143:
                basket = '01'
            elif 144 <= _short_id <= 287:
                basket = '02'
            elif 288 <= _short_id <= 431:
                basket = '03'
            elif 432 <= _short_id <= 719:
                basket = '04'
            elif 720 <= _short_id <= 1007:
                basket = '05'
            elif 1008 <= _short_id <= 1061:
                basket = '06'
            elif 1062 <= _short_id <= 1115:
                basket = '07'
            elif 1116 <= _short_id <= 1169:
                basket = '08'
            elif 1170 <= _short_id <= 1313:
                basket = '09'
            elif 1314 <= _short_id <= 1601:
                basket = '10'
            elif 1602 <= _short_id <= 1655:
                basket = '11'
            elif 1656 <= _short_id <= 1919:
                basket = '12'
            elif 1920 <= _short_id <= 2045:
                basket = '13'
            elif 2046 <= _short_id <= 2189:
                basket = '14'
            elif 2190 <= _short_id <= 2405:
                basket = '15'
            else:
                basket = '16'

            response2 = requests.get(f'https://basket-{basket}.wbbasket.ru/vol{_short_id}/part{item_id // 1000}/{item_id}/info/ru/card.json')
            result = response2.json().get('description')

            url2 = f"https://basket-{basket}.wbbasket.ru/vol{_short_id}/part{item_id // 1000}/{item_id}/images/big/1.webp"
            status_code = requests.get(url=url2).status_code
            if status_code == 200:
                link_str = ''.join([f'https://basket-{basket}.wbbasket.ru/vol{_short_id}/part{item_id // 1000}/{item_id}/images/big/{i}.webp\n' for i in range(1, min(10, pics) + 1)])

            else:
                print('Статус код равен: ', requests.get(url=url2).status_code)
                return False
        return name, old_price, price_with_discount, brand, item_id, rating_goods, link_str, feedbacks, result
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return False
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return False


def __get_item_id(url):
    if validators.url(url):
        regex = "(?<=catalog/).+(?=/detail)"
        match = re.search(regex, url)
        if match:
            return match[0]
    else:
        return url

    raise ValueError("Не удалось извлечь item_id из URL")


def writer_group_to_json(data, filename='groups.json'):
    try:
        # Читаем существующие данные
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    # Проверяем, существует ли группа с таким же username
    for group in existing_data:
        if group['username'] == data['username']:
            return False  # Возвращаем False, если дубликат найден

    # Добавляем новые данные
    existing_data.append(data)

    # Сохраняем обновленные данные
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4)

    return True


def remove_group_from_json(username, filename='groups.json'):
    try:
        # Читаем json файл
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        return False  # Файл не найден, возвращаем False

    # Ищем группу с указанным username
    for group in existing_data:
        if group['username'] == username:
            existing_data.remove(group)  # Удаляем группу
            # Сохраняем обновленные данные
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4)
            return True  # Возвращаем True, если группа была успешно удалена

    return False  # Возвращаем False, если группа с таким username не найдена


def load_from_json(filename='groups.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def vol_video_host(e):
    if 0 <= e <= 11:
        t = "01"
    elif e <= 23:
        t = "02"
    elif e <= 35:
        t = "03"
    elif e <= 47:
        t = "04"
    elif e <= 59:
        t = "05"
    elif e <= 71:
        t = "06"
    elif e <= 83:
        t = "07"
    elif e <= 95:
        t = "08"
    elif e <= 107:
        t = "09"
    elif e <= 119:
        t = "10"
    elif e <= 131:
        t = "11"
    elif e <= 143:
        t = "12"
    else:
        t = "13"

    return f"videonme-basket-{t}.wbbasket.ru"


def construct_host_v2(e, t="nm"):
    try:
        n = int(__get_item_id2(e))
    except ValueError:
        return None  # Возвращаем None, если не удалось преобразовать в int

    r = n % 144 if t == "video" else n // 100000
    o = n // 10000 if t == "video" else n // 1000

    if t == "video":
        s = vol_video_host(r)
        video_url = f"https://{s}/vol{r}/part{o}/{n}/mp4/360p/1.mp4"
        return video_url
    else:
        return None  # Возвращаем None для других типов


# Пример использования
def __get_item_id2(url):
    if validators.url(url):
        regex = "(?<=catalog/).+(?=/detail)"
        match = re.search(regex, url)
        if match:
            return match[0]
    else:
        return url

    raise ValueError("Не удалось извлечь item_id из URL")

# def checked_groups_db():
#     with open(f'{database_groups_file}', 'r', encoding='utf-8') as file:
#         file_read = file.read()
#         file_split = file_read.split('\n')
#
#         return file_split
#
#
# def add_group_db(group_name):
#     with open(f'{database_groups_file}', 'r', encoding='utf-8') as file:
#         file_read = file.read()
#         file_split = file_read.split('\n')
#         if group_name not in file_split:
#             with open(f'{database_groups_file}', 'a', encoding='utf-8') as file2:
#                 file2.write(f'\n{group_name}')
#                 return True
#
#         elif group_name in file_split:
#             return False
#
#         else:
#             print('Ошибка 77356-211')
#             return False
#
#
# def remove_group_db(group_name):
#     try:
#         with open(f'{database_groups_file}', 'r', encoding='utf-8') as file:
#             lines = [line.strip() for line in file.readlines()]
#
#         if group_name in lines:
#             lines.remove(group_name)
#             with open(f'{database_groups_file}', 'w', encoding='utf-8') as file:
#                 file.write('\n'.join(lines))
#             return True
#         else:
#             return False
#     except FileNotFoundError:
#         print(f"Файл '{database_groups_file}' не найден.")
#         return False
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
#         return False
#
#
# def read_group_file():
#     try:
#         keyboard = []
#         with open(f'{database_groups_file}', 'r', encoding='utf-8') as file:
#             file_read = file.read()
#             file_split = file_read.split('\n')
#             for i in file_split:
#                 keyboard.append([InlineKeyboardButton(text=f'{i}', url=f'https://t.me/{i}')])
#
#             keyboard_list = InlineKeyboardMarkup(inline_keyboard=keyboard)
#             return keyboard_list
#
#     except Exception as e:
#         print(f'Ошибка типа: {e} - (9990-0001)')
