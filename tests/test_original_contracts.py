import unittest
from unittest.mock import Mock, patch

from access import addresses
from access import requests as api_requests
from app import menus
from app.App import App
from app.input_validation import (
    VALIDATORS,
    validate_bank_code,
    validate_br_domain,
    validate_cptec_airport_code,
    validate_cptec_city,
    validate_cptec_city_code,
    validate_cep,
    validate_cnpj,
    validate_ddd,
    validate_holiday_year,
    validate_isbn,
)


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
        get.return_value = Mock(json=Mock(return_value=[{"name": "Banco A"}, {"name": "Banco B"}]))

        result = api_requests.open_dict("https://example.test/api/banks")

        self.assertEqual(result, [{"name": "Banco A"}, {"name": "Banco B"}])
        get.assert_called_once_with("https://example.test/api/banks", timeout=10)

    @patch("access.requests.requests.get")
    def test_encodes_path_complement_safely(self, get):
        get.return_value = Mock(json=Mock(return_value={"ok": True}))
        api_requests.open_dict("https://example.test/api/banks/", " 01/A B?C ")
        get.assert_called_once_with("https://example.test/api/banks/01%2FA%20B%3FC", timeout=10)

    @patch("access.requests.requests.get")
    def test_timeout_is_explicit_and_propagated(self, get):
        failure = api_requests.requests.exceptions.Timeout("slow")
        get.side_effect = failure
        with self.assertRaises(api_requests.requests.exceptions.Timeout) as raised:
            api_requests.open_dict("https://example.test/api/banks")
        self.assertIs(raised.exception, failure)
        get.assert_called_once_with("https://example.test/api/banks", timeout=10)

    @patch("access.requests.requests.get")
    def test_raises_for_http_error_response(self, get):
        response = Mock()
        response.raise_for_status.side_effect = api_requests.requests.exceptions.HTTPError("bad status")
        get.return_value = response
        with self.assertRaises(api_requests.requests.exceptions.HTTPError):
            api_requests.open_dict("https://example.test/api/banks")
        response.json.assert_not_called()

    @patch("access.requests.requests.get")
    def test_propagates_invalid_json_failure(self, get):
        failure = api_requests.requests.exceptions.JSONDecodeError("invalid", "{", 0)
        response = Mock()
        response.json.side_effect = failure
        get.return_value = response
        with self.assertRaises(api_requests.requests.exceptions.JSONDecodeError) as raised:
            api_requests.open_dict("https://example.test/api/banks")
        self.assertIs(raised.exception, failure)

    @patch("access.requests.requests.get")
    def test_decodes_json_dictionary_and_appends_page(self, get):
        get.return_value = Mock(json=Mock(return_value={"code": "001", "name": "Banco A"}))

        result = api_requests.open_dict("https://example.test/api/banks", "001")

        self.assertEqual(result, {"code": "001", "name": "Banco A"})
        get.assert_called_once_with("https://example.test/api/banks/001", timeout=10)

    @patch("access.requests.requests.get")
    def test_propagates_connection_failure(self, get):
        failure = api_requests.requests.exceptions.ConnectionError("offline")
        get.side_effect = failure

        with self.assertRaises(api_requests.requests.exceptions.ConnectionError) as raised:
            api_requests.open_dict("https://example.test/api/banks")

        self.assertIs(raised.exception, failure)
        get.assert_called_once_with("https://example.test/api/banks", timeout=10)


class InputValidationTests(unittest.TestCase):
    def test_valid_values_and_cep_normalization(self):
        self.assertEqual(validate_cep("12345-678"), "12345678")
        self.assertEqual(validate_cep("12345678"), "12345678")
        self.assertEqual(validate_ddd("01"), "01")
        self.assertEqual(validate_holiday_year("0001"), "0001")
        self.assertEqual(validate_holiday_year("9999"), "9999")

    def test_cnpj_isbn_and_bank_code_normalization(self):
        self.assertEqual(validate_cnpj("12.abc.345/01de-35"), "12ABC34501DE35")
        self.assertEqual(validate_cnpj("12ABC34501DE35"), "12ABC34501DE35")
        self.assertEqual(validate_isbn("0-306-40615-2"), "0306406152")
        self.assertEqual(validate_isbn("978-0-306-40615-7"), "9780306406157")
        self.assertEqual(validate_isbn("0-8044-2957-x"), "080442957X")
        self.assertEqual(validate_bank_code(" 001 "), "001")
        self.assertEqual(validate_bank_code("7"), "7")

    def test_brokerage_cnpj_reuses_existing_validator(self):
        self.assertIs(VALIDATORS["Corretoras por CNPJ"], validate_cnpj)
        self.assertEqual(VALIDATORS["Corretoras por CNPJ"](" 12.abc.345/01de-35 "), "12ABC34501DE35")
        with self.assertRaises(ValueError):
            VALIDATORS["Corretoras por CNPJ"]("12.abc.345/01de-3x")

    def test_br_domain_normalization_and_valid_values(self):
        self.assertIs(VALIDATORS["Busca por Dominio BR"], validate_br_domain)
        self.assertEqual(validate_br_domain("  WWW.Exemplo.BR "), "www.exemplo.br")
        self.assertEqual(validate_br_domain("ação.br"), "ação.br")
        self.assertEqual(validate_br_domain("xn--ao-6ja.br"), "xn--ao-6ja.br")

    def test_br_domain_rejects_invalid_values(self):
        for value in (
            "", "   ", "exemplo", "exemplo.com", "https://exemplo.br",
            "http://exemplo.br", "exemplo.br/path", "exemplo.br?x=1",
            "exemplo.br#fragment", ".br", "-exemplo.br", "exemplo-.br",
            "\U0001f600.br", "\u0080.br", "a\u200d.br", "\u0301a.br",
            "exemplo..br", "exemplo_br", "exemplo br",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_br_domain(value)

    def test_cptec_valid_values_and_normalization(self):
        self.assertEqual(validate_cptec_city("  São José dos Campos  "), "São José dos Campos")
        self.assertEqual(validate_cptec_city("  Rio  de Janeiro "), "Rio  de Janeiro")
        self.assertEqual(validate_cptec_airport_code("  sbgr "), "SBGR")
        self.assertEqual(validate_cptec_airport_code("KJFK"), "KJFK")
        self.assertEqual(validate_cptec_city_code(" 001 "), "001")
        self.assertEqual(validate_cptec_city_code("123456789012345"), "123456789012345")

    def test_cptec_rejects_invalid_values(self):
        for validator, values in (
            (validate_cptec_city, ("", "   ", "Rio\n de Janeiro", "São\x00Paulo")),
            (validate_cptec_airport_code, ("", "ABC", "ABCDE", "AB1D", "ÁBCD", "ＡBCD")),
            (validate_cptec_city_code, ("", "   ", "0", "000", "-1", "+1", "1.0", "١٢")),
        ):
            for value in values:
                with self.subTest(validator=validator.__name__, value=value), self.assertRaises(ValueError):
                    validator(value)

    def test_cptec_validators_are_registered_and_parameterless_operations_are_not(self):
        self.assertIs(VALIDATORS["CPTEC por cidade"], validate_cptec_city)
        self.assertIs(VALIDATORS["Clima em aeroportos por codigo"], validate_cptec_airport_code)
        self.assertIs(VALIDATORS["Clima em cidade por codigo"], validate_cptec_city_code)
        self.assertIs(VALIDATORS["Onda em cidade por codigo"], validate_cptec_city_code)
        self.assertNotIn("Cidades da CPTEC", VALIDATORS)
        self.assertNotIn("Clima em capitais", VALIDATORS)

    def test_cnpj_isbn_and_bank_code_reject_invalid_values(self):
        cases = (
            (validate_cnpj, "12.abc.345/01de-3x"),
            (validate_cnpj, "12.abc.345/01de_35"),
            (validate_cnpj, "１２ABC34501DE35"),
            (validate_isbn, "123456789"),
            (validate_isbn, "123456789X0"),
            (validate_isbn, "978030640615X"),
            (validate_isbn, "978030640615"),
            (validate_bank_code, ""),
            (validate_bank_code, "1234"),
            (validate_bank_code, "1a"),
            (validate_bank_code, "１２"),
        )
        for validator, value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validator(value)

    def test_new_validators_are_registered_under_existing_operation_names(self):
        self.assertIs(VALIDATORS["Busca por CNPJ"], validate_cnpj)
        self.assertIs(VALIDATORS["Busca Livro por ISNB"], validate_isbn)
        self.assertIs(VALIDATORS["Banco por codigo"], validate_bank_code)
        self.assertIs(VALIDATORS["Corretoras por CNPJ"], validate_cnpj)
        self.assertIs(VALIDATORS["Busca por Dominio BR"], validate_br_domain)

    def test_invalid_values(self):
        cases = (
            (validate_cep, "1234-5678"), (validate_cep, "1234567"),
            (validate_cep, "12345--678"), (validate_ddd, "1"),
            (validate_ddd, "001"), (validate_holiday_year, "0000"),
            (validate_holiday_year, "202"), (validate_holiday_year, "20a4"),
        )
        for validator, value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validator(value)

    @patch("app.App.open_dict")
    def test_rejected_input_does_not_call_http_client(self, open_dict):
        for operation, value in (
            ("Busca por CEP", "123"),
            ("Busca por CNPJ", "12ABC34501DE3X"),
            ("Busca Livro por ISNB", "123456789"),
            ("Banco por codigo", "1234"),
            ("Corretoras por CNPJ", "12ABC34501DE3X"),
            ("Busca por Dominio BR", "https://exemplo.br"),
            ("CPTEC por cidade", "  \n  "),
            ("CPTEC por cidade", "Rio\x00Janeiro"),
            ("Clima em aeroportos por codigo", "AB1D"),
            ("Clima em cidade por codigo", "0"),
            ("Onda em cidade por codigo", "１２３"),
        ):
            with self.subTest(operation=operation):
                open_dict.reset_mock()
                app = App.__new__(App)
                app.selected_operation = operation
                app.field_toplevel = Mock()
                app.clear = Mock()
                app.print_text = Mock()
                app.print_entry = Mock()
                app.listbox_right = Mock()
                app.api_address = "https://example.test/api"

                app._get_to_quick_window(Mock(get=Mock(return_value=value)))

                open_dict.assert_not_called()
                app.print_text.assert_called_once()
                app.field_toplevel.destroy.assert_called_once()

    def test_cptec_rejects_controls_at_edges(self):
        for value in ("Rio\n", "\tRio", "Rio\t", "Rio\r"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    validate_cptec_city(value)

    @patch("app.App.open_dict")
    def test_parameterless_cptec_operations_use_search(self, open_dict):
        for operation in ("Cidades da CPTEC", "Clima em capitais"):
            with self.subTest(operation=operation):
                open_dict.reset_mock()
                open_dict.return_value = ["ok"]

                app = App.__new__(App)
                app.listbox_left = Mock()
                app.listbox_left.get.return_value = operation
                app.dict_selected = addresses.cptec_meteorology
                app.clear = Mock()
                app.print_text = Mock()
                app.print_entry = Mock()
                app.listbox_right = Mock()
                app._quick_window = Mock()

                app.search()

                expected_url = addresses.cptec_meteorology[operation][0]
                open_dict.assert_called_once_with(expected_url)
                app._quick_window.assert_not_called()

if __name__ == "__main__":
    unittest.main()
