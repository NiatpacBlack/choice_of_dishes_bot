from unittest import TestCase, main

from firebase_admin import firestore

from db import FirestoreClient
from exceptions import CollectionArgumentError, CollectionArgumentTypeError


class FirestoreClientTest(TestCase):
    """Для работы этих тестов в базе данных должны быть коллекция menu и документ drinks."""

    def setUp(self):
        self.firestore_client = FirestoreClient()
        self.document = self.firestore_client.db_client.collection('menu').document('drinks')
        self.collection = self.firestore_client.db_client.collection('menu')

    def test_add_document(self):
        """Тестируем добавление нового документа в коллекцию firebase."""

        # Удалим тестовый документ, на случай если он есть в коллекции.
        self.collection.document("testTEST999").delete()

        # Получаем количество всех документов в коллекции и проверяем что такого названия нет в документах.
        documents_count = len(list(self.collection.stream()))
        self.assertEqual("testTEST999" in [doc.id for doc in self.collection.stream()], False)

        # Производим добавление нового документа.
        self.firestore_client.add_document('menu', 'testTEST999')

        # Проверяем, увеличилось ли количество документов после добавления нового.
        self.assertEqual(len(list(self.collection.stream())), documents_count + 1)

        # Проверяем, что документ с таким именем действительно появился в выборке.
        self.assertEqual("testTEST999" in [doc.id for doc in self.collection.stream()], True)

        # Удаляем тестовый документ.
        self.collection.document("testTEST999").delete()

    def test_delete_document(self):
        """Тестируем удаление документа из коллекции firebase."""

        # Добавляем тестовый документ в коллекцию.
        self.firestore_client.add_document('menu', 'testTEST999')

        # Проверяем, что документ с таким именем действительно появился в выборке всех документов.
        self.assertEqual("testTEST999" in [doc.id for doc in self.collection.stream()], True)

        # Получаем количество всех документов в коллекции.
        documents_count = len(list(self.collection.stream()))

        # Производим удаление документа.
        self.firestore_client.delete_document(collection_name='menu', document_name='testTEST999')

        # Проверяем, уменьшилось ли количество документов после удаление.
        self.assertEqual(len(list(self.collection.stream())), documents_count - 1)

        # Проверяем, есть ли документ с таким названием в выборке.
        self.assertEqual("testTEST999" in [doc.id for doc in self.collection.stream()], False)

    def test_add_valid_product_in_document(self):
        """1 тест. Проверка всех возможных правильных вариантов переданных данных."""

        test = {'TEST1': {'description': 'TEST1TEST1TEST1TEST1', 'price': 2195812519512, 'in_active': False}}
        test2 = {'TEST2': {'description': 'TEST2TEST2TEST2TEST2', 'price': 2195812519512.12}}
        test2_2 = {'TEST2_2': {'price': 2195812519512.12}}
        test2_3 = {'TEST2_3': {'price': 2195812519512.12, 'in_active': False}}

        valid_tests = (test, test2, test2_2, test2_3)

        for test in valid_tests:
            product_name = str(*test.keys())

            # Проверяем что тестового продукта нет в списке продуктов.
            self.assertEqual(product_name not in self._get_all_product_names(), True)

            # Добавляем продукт в документ.
            self.firestore_client.add_product(collection_name='menu', document_name='drinks', data=test)

            # Проверяем что тестовый продукт появился в списке продуктов.
            self.assertEqual(product_name in self._get_all_product_names(), True)

            # Удаляем тестовый продукт.
            self.document.update({product_name: firestore.DELETE_FIELD})

    def test_add_invalid_product_in_document(self):
        """2 тест. Проверка всех возможных неправильных вариантов переданных данных."""

        test3 = 13
        test4 = {'TEST4': {'description': 'Газированный сладкий напиток', 'price': 'str_price'}}
        test5 = {'TEST5': {'description': 124, 'price': 'str_price'}}
        test6 = {'TEST6': {'description': '', 'price': 1, 'new_price': 123, 'new_new_price': 124125}}
        test7 = {'ТЕСТ7': {}}
        test8 = {}
        test9 = {123}

        invalid_tests = (test3, test6, test7, test8, test9)
        invalid_type_tests = (test4, test5)

        for test in invalid_tests:
            with self.assertRaises(CollectionArgumentError) as e:
                self.firestore_client.add_product(collection_name='menu', document_name='drinks', data=test)
                self.assertEqual(
                    'В data переданы неверные аргументы или пустой шаблон, сверьтесь с документацией метода.',
                    e.exception.args[0],
                )
        for test in invalid_type_tests:
            with self.assertRaises(CollectionArgumentTypeError) as e:
                self.firestore_client.add_product(collection_name='menu', document_name='drinks', data=test)
                self.assertEqual(
                    'Значения параметров продукта, не соответствует нужному типу данных.',
                    e.exception.args[0],
                )

    def test_return_get_all_products_from_document(self):
        """Тестируем функцию, которая получает данные из определенного документа."""

        # Если передана несуществующая коллекция.
        self.assertEqual(self.firestore_client.get_all_products_from_document('m!enu15125125', 'drinks'), None)

        # Если передан несуществующий документ.
        self.assertEqual(self.firestore_client.get_all_products_from_document('menu', 'drin123ks'), None)

        # Если переданы верные параметры, функция должна вернуть словарь.
        self.assertEqual(type(self.firestore_client.get_all_products_from_document('menu', 'drinks')), dict)

    def test_delete_product_from_document(self):
        """Тест функции удаления товара из документа."""

        new_product = {'Тесттест998': {'description': 'Тестовое описание', 'price': 1.50}}

        # Добавляем тестовый товар new_product в документ.
        self.document.set(new_product, merge=True)

        all_products = self.document.get().to_dict()

        # Проверяем что товар с таким названием действительно есть в документе.
        self.assertEqual('Тесттест998' in tuple(all_products.keys()), True)

        # Получаем общее число всех товаров в документе.
        products_count = len(all_products)

        # Удаляем товар из документа.
        self.firestore_client.delete_product(collection_name='menu', document_name="drinks", product_name='Тесттест998')

        # Проверяем, что число товаром уменьшилось на 1.
        self.assertEqual(len(self.document.get().to_dict()), products_count - 1)

        # Проверяем, что товара с таким названием больше нет в списке названий товаров.
        self.assertEqual('Тесттест998' in tuple(self.document.get().to_dict().keys()), False)

    def _get_all_product_names(self):
        return [product_name for product_name in self.document.get().to_dict()]


if __name__ == '__main__':
    main()
