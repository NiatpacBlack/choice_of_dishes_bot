from pprint import pprint

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from bot_app import os
from exceptions import CollectionArgumentError, NoProductNameError, CollectionArgumentTypeError


class FirestoreClient:
    """Класс для подключения и работы с базой данных FireBase."""

    # Подключение к базе данных
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    firebase_admin.initialize_app(cred, {"projectId": os.getenv('DATABASE_ID')})

    def __init__(self):
        self.db_client = firestore.client()

    def add_document(self, collection_name: str, document_name: str):
        """
        Создает новый документ с именем document_name в коллекции collection_name.

        Ничего не произойдет, если документ с таким именем уже существует или коллекции не существует.
        """

        return self.db_client.collection(collection_name).document(document_name).set({}, merge=True)

    def get_all_documents_from_collection(self, collection_name: str):
        """
        Возвращает все документы из коллекции collection_name.

        В результате мы получаем генератор с документами, название документа можно получить по свойству id,
        параметры документа можно получить методом to_dict() в виде словаря.
        """

        return self.db_client.collection(collection_name).stream()

    def delete_document(self, collection_name: str, document_name: str):
        """Удаляет весь документ document_name коллекции collection_name со всеми данными внутри."""

        return self.db_client.collection(collection_name).document(document_name).delete()

    def add_product(self, collection_name: str, document_name: str, data: dict):
        """
        Добавляет коллекцию data, содержащую название и свойства товара в документ document_name коллекции
        collection_name.
        Ключ главного словаря должен быть уникален, иначе данные существующей записи перезапишутся.
        Если document_name не существует, он создаст новый документ с таким именем и запишет товар в него.

        Шаблон data: {'Sprite': {'description': 'Газированный сладкий напиток', 'price': 2.82}}

        По умолчанию во внутренний словарь параметров будет добавлено свойство 'in active': True, но его можно
        также передать дополнительным аргументом:
        {'Sprite': {'description': 'Газированный сладкий напиток', 'price': 2.82, 'in_active': False}}
        """

        try:
            data = self._template_product_validator(product=data)
        except ValueError or AttributeError:
            raise CollectionArgumentError(
                'В data переданы неверные аргументы или пустой шаблон, сверьтесь с документацией метода.'
            )
        try:
            self._type_product_validator(product_parameters=data[tuple(data.keys())[0]])
        except TypeError:
            raise CollectionArgumentTypeError('Значения параметров продукта, не соответствует нужному типу данных.')

        return self.db_client.collection(collection_name).document(document_name).set(data, merge=True)

    def get_all_products_from_document(self, collection_name: str, document_name: str) -> dict | None:
        """Получает все данные из документа document_name из коллекции collection_name."""

        return self.db_client.collection(collection_name).document(document_name).get().to_dict()

    def delete_product(self, collection_name: str, document_name: str, product_name: str):
        """
        Удаляет продукт product_name из документа document_name коллекции collection_name.

        Если товара с таким названием нет, ничего не произойдет.
        """

        return self.db_client.collection(collection_name).document(document_name).update(
            {product_name: firestore.DELETE_FIELD}
        )

    def _update_product_property(self, collection_name: str, document_name: str, product_property: dict[str, any]):
        """
        Функция может изменить значение существующего параметра продукта или добавить новый параметр, если такого нет.

        Параметр должен быть словарем с ключом вида {'product_name.property_name': 25} и значением параметра любого типа
        """

        return self.db_client.collection(collection_name).document(document_name).update(product_property)

    @staticmethod
    def _template_product_validator(product: dict) -> dict:
        """
        Проверяет переданный словарь данных с информацией о продукте, на соответствие шаблону добавления в документ.
        """

        if type(product) != dict or len(product) != 1:
            raise ValueError

        product_name = tuple(product.keys())[0]
        inner_keys_from_product = tuple(product[product_name].keys())

        valid_parameters = (
            ('price',), ('description', 'price'), ('price', 'in_active'), ('description', 'price', 'in_active')
        )

        if inner_keys_from_product in valid_parameters:
            if 'description' not in inner_keys_from_product:
                product[product_name]['description'] = ''
            if 'in_active' not in inner_keys_from_product:
                product[product_name]['in_active'] = True
            return product
        else:
            raise ValueError

    @staticmethod
    def _type_product_validator(product_parameters: dict) -> None:
        """
        Проверяет определенные значения переданного словаря, на соответствие нужному типу данных.
        Внутренний метод добавления продукта в документ.
        """
        try:
            if any((type(product_parameters['price']) not in (int, float),
                    type(product_parameters['description']) != str,
                    type(product_parameters['in_active']) != bool)):
                raise TypeError
        except KeyError:
            raise KeyError("Переданные данные не соответствуют шаблону. Сверьтесь с документацией к add_product")


if __name__ == '__main__':
    firestore_client = FirestoreClient()



