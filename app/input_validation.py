"""Small input validators for structured operation inputs."""

import re
import unicodedata


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


def validate_br_domain(value):
    """Validate a conservative .br hostname shape; registration is not checked.

    Unicode letters are accepted for internationalized labels. DNS byte-length,
    IDNA conversion and BrasilAPI registration/availability are left to the API.
    """
    value = value.strip().lower()
    label = r"[a-z0-9\u0080-\U0010ffff](?:[a-z0-9\u0080-\U0010ffff-]*[a-z0-9\u0080-\U0010ffff])?"
    invalid_character = any(
        ch not in ".-"
        and unicodedata.category(ch)[0] not in ("L", "M")
        and unicodedata.category(ch) != "Nd"
        for ch in value
    )
    invalid_start = any(
        part and unicodedata.category(part[0])[0] == "M"
        for part in value.split(".")
    )
    if re.fullmatch(rf"{label}(?:\.{label})*\.br", value) is None or invalid_character or invalid_start:
        raise ValueError("Domínio .br inválido. Informe apenas um nome de domínio terminado em .br.")
    return value


def validate_cptec_city(value):
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        raise ValueError("Cidade inválida. Informe o nome sem caracteres de controle.")

    value = value.strip()
    if not value:
        raise ValueError("Cidade inválida. Informe o nome da cidade.")

    return value


def validate_cptec_airport_code(value):
    value = value.strip()
    if re.fullmatch(r"[A-Za-z]{4}", value) is None:
        raise ValueError("Código de aeroporto inválido. Informe quatro letras ASCII.")
    return value.upper()


def validate_cptec_city_code(value):
    value = value.strip()
    if re.fullmatch(r"[0-9]+", value) is None or not any(ch != "0" for ch in value):
        raise ValueError("Código de cidade inválido. Informe um código numérico positivo.")
    return value


def validate_fipe_vehicle_type(value):
    value = value.strip().lower()
    if value not in ("", "carros", "motos", "caminhoes"):
        raise ValueError("Tipo de veiculo FIPE invalido. Informe carros, motos ou caminhoes.")
    return value


def validate_fipe_code(value):
    value = value.strip()
    if re.fullmatch(r"[0-9]{6}-[0-9]", value) is None:
        raise ValueError("Codigo FIPE invalido. Informe apenas digitos e, opcionalmente, um hifen.")
    return value


VALIDATORS = {
    "Busca por CEP": validate_cep,
    "Busca por DDD": validate_ddd,
    "Feriados por ano": validate_holiday_year,
    "Busca por CNPJ": validate_cnpj,
    "Busca Livro por ISNB": validate_isbn,
    "Banco por codigo": validate_bank_code,
    "Corretoras por CNPJ": validate_cnpj,
    "Busca por Dominio BR": validate_br_domain,
    "CPTEC por cidade": validate_cptec_city,
    "Clima em aeroportos por codigo": validate_cptec_airport_code,
    "Clima em cidade por codigo": validate_cptec_city_code,
    "Onda em cidade por codigo": validate_cptec_city_code,
    "Marcas por caminhoes, carros ou moto": validate_fipe_vehicle_type,
    "Preco de veiculo por codigo FIPE": validate_fipe_code,
}
