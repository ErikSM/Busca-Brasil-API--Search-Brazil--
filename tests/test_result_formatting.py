import unittest
from copy import deepcopy

from app.result_formatting import format_result


class ResultFormattingTests(unittest.TestCase):
    def test_dictionary_order_and_numbers(self):
        self.assertEqual(format_result({"z": 0, "a": -2.5}), ["z: 0", "a: -2.5"])

    def test_list_of_dictionaries(self):
        self.assertEqual(format_result([{"nome": "A"}, {"nome": "B"}]),
                         ["1.", "  nome: A", "2.", "  nome: B"])

    def test_nested_dictionary(self):
        self.assertEqual(format_result({"endereco": {"cidade": "São Paulo"}}),
                         ["endereco:", "  cidade: São Paulo"])

    def test_nested_lists_and_mixed_values(self):
        self.assertEqual(format_result({"itens": [1, ["A"], {"x": 2}]}),
                         ["itens:", "  1. 1", "  2.", "    1. A", "  3.", "    x: 2"])

    def test_null_and_booleans(self):
        self.assertEqual(format_result({"n": None, "sim": True, "nao": False}),
                         ["n: Não informado", "sim: Sim", "nao: Não"])

    def test_empty_results(self):
        for value, expected in [({}, "Objeto vazio"), ([], "Lista vazia"),
                                ("", "Texto vazio"), (None, "Não informado")]:
            with self.subTest(value=value):
                self.assertEqual(format_result(value), [expected])

    def test_nested_empty_values(self):
        self.assertEqual(format_result({"obj": {}, "lista": [], "texto": ""}),
                         ["obj: Objeto vazio", "lista: Lista vazia", "texto: Texto vazio"])

    def test_unicode_and_multiline_text(self):
        self.assertEqual(format_result({"ação": "Olá 🌎\n日本"}),
                         ["ação: Olá 🌎", "  日本"])

    def test_simple_values(self):
        for value, expected in [(0, "0"), (False, "Não"), (3.5, "3.5"), ("São Luís", "São Luís")]:
            with self.subTest(value=value):
                self.assertEqual(format_result(value), [expected])

    def test_does_not_mutate_input(self):
        value = {"b": [{"x": [None, False, 0]}], "a": "ação"}
        original = deepcopy(value)
        child = value["b"][0]["x"]
        format_result(value)
        self.assertEqual(value, original)
        self.assertEqual(list(value), ["b", "a"])
        self.assertIs(value["b"][0]["x"], child)

    def test_large_results_are_not_truncated(self):
        lines = format_result(list(range(2000)))
        self.assertEqual(len(lines), 2000)
        self.assertEqual(lines[0], "1. 0")
        self.assertEqual(lines[-1], "2000. 1999")
