"""Plain display lines for JSON values, independent of Tkinter.

Order and all results are preserved. Formatting and widget insertion remain
synchronous: very large responses may occupy the UI thread and memory.
Batching/virtualization belongs to stage 05B.2. Deep nesting is bounded by
Python's recursion limit; inputs are JSON trees, not cyclic Python objects.
"""


def format_result(value):
    """Return readable lines without changing the supplied JSON tree."""
    lines = []

    def append(item, depth=0, prefix=""):
        indent = "  " * depth
        if isinstance(item, (dict, list)) and item:
            if prefix:
                lines.append(indent + prefix.rstrip())
                depth += 1
            if isinstance(item, dict):
                for key, child in item.items():
                    append(child, depth, str(key) + ": ")
            else:
                for number, child in enumerate(item, 1):
                    append(child, depth, f"{number}. ")
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
        parts = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        lines.append(indent + prefix + parts[0])
        lines.extend(indent + "  " + part for part in parts[1:])

    append(value)
    return lines
