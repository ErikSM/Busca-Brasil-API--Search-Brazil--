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


VALIDATORS = {
    "Busca por CEP": validate_cep,
    "Busca por DDD": validate_ddd,
    "Feriados por ano": validate_holiday_year,
}
