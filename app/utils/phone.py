import re

PHONE_SYMBOLS = "+1234567890()-"


def phone_to_text(phone: str) -> str:
    phone = phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")

    if phone.startswith("8"):
        phone = phone.replace("8", "+7", 1)
    elif phone.startswith("7"):
        phone = phone.replace("7", "+7", 1)
    return phone


def is_phone_correct(phone: str) -> bool:
    phone = phone_to_text(phone)

    return bool(re.match(r"\+7\d{10}$", phone))


def format_phone(phone: str) -> str:
    phone_pattern = re.compile(r"(\+7)(\d{3})(\d{3})(\d{2})(\d{2})")
    format_pattern = r"\1(\2)\3-\4-\5"
    formatted_phone = re.sub(phone_pattern, format_pattern, phone)
    return formatted_phone
