import unittest
from copy import deepcopy

from app.result_formatting import format_result, iter_format_result


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


class IncrementalFormattingTests(unittest.TestCase):
    def test_equivalence_order_values_and_no_mutation(self):
        values = [None, False, True, 0, {}, [], "", "Olá 🌎\r\n日本\rfim\n",
                  {"z": [None, False, True, 0, {}, [], ""],
                   "a": {"ação": ["Olá\n日本", [1, 2]]}}]
        original = deepcopy(values)
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(list(iter_format_result(value)), format_result(value))
        self.assertEqual(values, original)
        self.assertEqual(list(values[-1]), ["z", "a"])

    def test_multiline_boundaries_preserve_empty_and_unicode_lines(self):
        self.assertEqual(list(iter_format_result({"ação": "\r\nOlá\r日本\n\n"})),
                         ["ação: ", "  Olá", "  日本", "  ", "  "])
        self.assertEqual(list(iter_format_result("a\vb\fc\u2028d")), ["a\vb\fc\u2028d"])

    def test_list_is_read_only_as_lines_are_requested(self):
        visited = []

        class ObservedList(list):
            def __iter__(self):
                for item in super().__iter__():
                    visited.append(item)
                    yield item

        lines = iter_format_result(ObservedList(range(10000)))
        self.assertEqual(visited, [])
        self.assertIs(iter(lines), lines)
        self.assertEqual(next(lines), "1. 0")
        self.assertEqual(visited, [0])
        self.assertEqual(next(lines), "2. 1")
        self.assertEqual(visited, [0, 1])

    def test_nested_dictionary_is_not_read_ahead(self):
        visited = []

        class ObservedDict(dict):
            def items(self):
                for key, value in super().items():
                    visited.append(key)
                    yield key, value

        lines = iter_format_result({"nested": ObservedDict(first=0, last=False)})
        self.assertEqual(next(lines), "nested:")
        self.assertEqual(visited, [])
        self.assertEqual(next(lines), "  first: 0")
        self.assertEqual(visited, ["first"])
        self.assertEqual(list(lines), ["  last: Não"])

    def test_multiline_string_does_not_split_or_copy_whole_text(self):
        class ObservedText(str):
            def split(self, *args, **kwargs):
                raise AssertionError("Eager split")

            def replace(self, *args, **kwargs):
                raise AssertionError("Whole text copied")

            def __str__(self):
                return self

        lines = iter_format_result(ObservedText("primeira\r\n" + "outra\n" * 10000))
        self.assertEqual(next(lines), "primeira")
        self.assertEqual(next(lines), "  outra")

    def test_ten_thousand_nested_records_are_complete_and_ordered(self):
        value = [{"id": n, "ativo": False} for n in range(10000)]
        expected = [line for n in range(10000)
                    for line in (f"{n + 1}.", f"  id: {n}", "  ativo: Não")]
        self.assertEqual(list(iter_format_result(value)), expected)
