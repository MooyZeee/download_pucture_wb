import re

import requests


def get_product_info(url):
    try:
        item_id = __get_item_id(url)
        print(f"Извлеченный item_id: {item_id}")  # Выводим item_id для проверки
        response = requests.get(
            f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={item_id}")
        print(response.url)
        data = response.json()

        if "data" not in data or "products" not in data["data"] or not data["data"]["products"]:
            print("Нет данных о товаре.")
            return

        product = data["data"]["products"][0]

        name = product.get("name")
        brand = product.get("brand")
        old_price = product.get("salePriceU") / 100
        discrout_result = (3 / 100) * old_price
        price_with_discount = old_price - discrout_result
        image_link = product.get("image")

    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def __get_item_id(url):
    regex = "(?<=catalog/).+(?=/detail)"
    match = re.search(regex, url)
    if match:
        return match[0]
    raise ValueError("Не удалось извлечь item_id из URL")


if __name__ == "__main__":
    product_url = input("Введите ссылку на товар Wildberries: ")
    get_product_info(product_url)
