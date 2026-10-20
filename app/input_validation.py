"""Small input validators for structured operation inputs."""

import re


def validate_cep(value):
    value = value.strip()
    if re.fullmatch(r"[0-9]{5}-?[0-9]{3}", value) is None:
        raise ValueError("CEP inválido. Informe oito dígitos, com ou sem hífen.")
    return value.replace("-", "")


def validate_ddd(value):
    value = value.strip()
    if re.fullmatch(r"[0-9]{2}", value) is None:
        raise ValueError("DDD inválido. Informe exatamente dois dígitos.")
    return value


def validate_holiday_year(value):
    value = value.strip()
    if re.fullmatch(r"[0-9]{4}", value) is None or int(value) == 0:
        raise ValueError("Ano inválido. Informe um ano válido com quatro dígitos.")
    return value


def validate_cnpj(value):
    value = value.strip().upper()
    if re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", value.replace(".", "").replace("/", "").replace("-", "")) is None:
        raise ValueError("CNPJ inválido. Informe 12 caracteres alfanuméricos e dois dígitos finais.")
    return value.replace(".", "").replace("/", "").replace("-", "")


def validate_isbn(value):
    value = value.strip().upper()
    normalized = value.replace("-", "")
    if re.fullmatch(r"(?:[0-9]{9}[0-9X]|[0-9]{13})", normalized) is None:
        raise ValueError("ISBN inválido. Informe ISBN-10 ou ISBN-13, com ou sem hífens.")
    return normalized


def validate_bank_code(value):
    value = value.strip()
    if re.fullmatch(r"[0-9]{1,3}", value) is None:
        raise ValueError("Código bancário inválido. Informe de um a três dígitos.")
    return value


VALIDATORS = {
    "Busca por CEP": validate_cep,
    "Busca por DDD": validate_ddd,
    "Feriados por ano": validate_holiday_year,
    "Busca por CNPJ": validate_cnpj,
    "Busca Livro por ISNB": validate_isbn,
    "Banco por codigo": validate_bank_code,
}
