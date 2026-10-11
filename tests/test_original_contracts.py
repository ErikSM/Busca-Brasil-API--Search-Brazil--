import unittest
from unittest.mock import Mock, patch

from access import addresses
from access import requests as api_requests
from app import menus


class CatalogTests(unittest.TestCase):
    def test_eight_categories_and_twenty_four_operations_are_registered(self):
        expected_categories = {
            "Bank/Stockbroker",
            "Address/Register",
            "Meteorology(CPTEC)",
            "Holidays",
            "Vehicles(FIPE)",
            "Books(ISNB)",
            "Products(NCM)",
            "Taxes",
        }
        self.assertEqual(set(menus.menus_list), expected_categories)
        self.assertEqual(sum(len(operations) for operations, _ in menus.menus_list.values()), 24)
        self.assertEqual(
            {id(operations) for operations, _ in menus.menus_list.values()},
            {
                id(addresses.bank_and_stockbroker),
                id(addresses.address_and_register),
                id(addresses.cptec_meteorology),
                id(addresses.holidays),
                id(addresses.fipe_vehicles),
                id(addresses.isnb_books),
                id(addresses.ncm_products),
                id(addresses.taxes),
            },
        )

    def test_endpoint_definitions_are_well_formed(self):
        for category_name, (operations, _description) in menus.menus_list.items():
            with self.subTest(category=category_name):
                self.assertIsInstance(operations, dict)
                for operation_name, definition in operations.items():
                    with self.subTest(operation=operation_name):
                        self.assertIsInstance(definition, tuple)
                        self.assertEqual(len(definition), 3)
                        url, needs_complement, description = definition
                        self.assertRegex(url, r"^https://brasilapi\.com\.br/api/.+")
                        self.assertIs(type(needs_complement), bool)
                        self.assertIsInstance(description, str)
                        self.assertTrue(description.strip())


class OpenDictTests(unittest.TestCase):
    @patch("access.requests.requests.get")
    def test_decodes_json_list(self, get):
        get.return_value = Mock(text='[{"name": "Banco A"}, {"name": "Banco B"}]')

        result = api_requests.open_dict("https://example.test/api/banks")

        self.assertEqual(result, [{"name": "Banco A"}, {"name": "Banco B"}])
        get.assert_called_once_with("https://example.test/api/banks/")

    @patch("access.requests.requests.get")
    def test_decodes_json_dictionary_and_appends_page(self, get):
        get.return_value = Mock(text='{"code": "001", "name": "Banco A"}')

        result = api_requests.open_dict("https://example.test/api/banks", "001")

        self.assertEqual(result, {"code": "001", "name": "Banco A"})
        get.assert_called_once_with("https://example.test/api/banks/001")

    @patch("access.requests.requests.get")
    def test_propagates_connection_failure(self, get):
        failure = api_requests.requests.exceptions.ConnectionError("offline")
        get.side_effect = failure

        with self.assertRaises(api_requests.requests.exceptions.ConnectionError) as raised:
            api_requests.open_dict("https://example.test/api/banks")

        self.assertIs(raised.exception, failure)
        get.assert_called_once_with("https://example.test/api/banks/")


if __name__ == "__main__":
    unittest.main()
