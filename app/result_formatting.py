"""Plain display lines for JSON values, independent of Tkinter.

Order and all results are preserved, with lines generated on demand.
Deep nesting is bounded by Python's recursion limit; inputs are JSON trees,
not cyclic Python objects.
"""


import re


def format_result(value):
    """Return readable lines without changing the supplied JSON tree."""
    return list(iter_format_result(value))


def iter_format_result(value):
    """Yield display lines without materializing the result or multiline strings."""
    yield from _iter_lines(value)


def _iter_lines(item, depth=0, prefix=""):
    indent = "  " * depth
    if isinstance(item, (dict, list)) and item:
        if prefix:
            yield indent + prefix.rstrip()
            depth += 1
        if isinstance(item, dict):
            for key, child in item.items():
                yield from _iter_lines(child, depth, str(key) + ": ")
        else:
            for number, child in enumerate(item, 1):
                yield from _iter_lines(child, depth, f"{number}. ")
        return
    if item is None:
        text = "Não informado"
    elif isinstance(item, bool):
        text = "Sim" if item else "Não"
    elif isinstance(item, dict):
        text = "Objeto vazio"
    elif isinstance(item, list):
        text = "Lista vazia"
    elif item == "":
        text = "Texto vazio"
    else:
        text = str(item)
    # Scan one separator at a time, including empty and trailing lines.
    start = 0
    for separator in re.finditer(r"\r\n|\r|\n", text):
        yield indent + prefix + text[start:separator.start()]
        prefix = "  "
        start = separator.end()
    yield indent + prefix + text[start:]
