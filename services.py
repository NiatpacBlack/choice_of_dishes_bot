from db import FirestoreClient
from telebot import types

firestore_client = FirestoreClient()


def get_all_categories_names() -> list:
    """Возвращает список с названиями всех категорий из базы данных."""

    return [doc.id for doc in firestore_client.get_all_documents_from_collection(collection_name='menu')]


def get_all_dishes_names(category: str) -> any:
    pass


def create_start_keyboard():
    """ Создает кнопки выпадающие при старте бота """

    start_keyboard = types.InlineKeyboardMarkup()
    menu_btn = types.InlineKeyboardButton(text="Меню", callback_data='menu')
    admin_btn = types.InlineKeyboardButton(text="Панель администратора", callback_data='admin')
    start_keyboard.add(menu_btn)
    start_keyboard.add(admin_btn)
    return start_keyboard


def create_category_keyboard():
    """Создает кнопки соответствующие каждой активной категории из базы данных."""

    buttons = get_all_categories_names()
    category_keyboard = types.InlineKeyboardMarkup()

    category_keyboard.add(types.InlineKeyboardButton(text='Back to start', callback_data='start'))

    for button in buttons:
        category_keyboard.add(types.InlineKeyboardButton(text=button, callback_data=button))

    return category_keyboard


def create_dishes_keyboard(category: str):
    """Создает кнопки соответствующие все блюдам в определенной категории."""

    dishes = list(
        firestore_client.get_all_products_from_document(collection_name='menu', document_name=category).keys())
    dishes_keyboard = types.InlineKeyboardMarkup()

    dishes_keyboard.add(types.InlineKeyboardButton(text='Back to categories', callback_data='menu'))

    for dish in dishes:
        dishes_keyboard.add(types.InlineKeyboardButton(text=dish, callback_data=dish))

    return dishes_keyboard


def create_back_to_categories_button():
    """Создает кнопку возврата к категориям."""

    keyboard = types.InlineKeyboardMarkup()
    back_keyboard = types.InlineKeyboardButton(text='Back to categories', callback_data='menu')
    keyboard.add(back_keyboard)
    return keyboard


def get_dishes_descriptions(category: str, dish: str):
    """Возвращает описание товара dish из категории category."""

    dishes = firestore_client.get_all_products_from_document(collection_name='menu', document_name=category)

    dish_description = dishes[dish]

    return f'{dish_description["description"]}: цена {dish_description["price"]}'


if __name__ == '__main__':

    for el in list(
            firestore_client.get_all_products_from_document(collection_name='menu', document_name='drinks').keys()):
        print(el, type(el))
