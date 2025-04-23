import hashlib
from typing import Any, Callable

from faker import Faker

fake = Faker()


def fake_username(value: Any) -> str:
    return f"'{fake.unique.user_name()}'"


def fake_fullname(value: Any) -> str:
    return f"'{fake.unique.name()}'"


def fake_email(value: Any) -> str:
    hash_value = hashlib.md5(value.encode()).hexdigest()
    return f"'{hash_value}@pyrify.com'"


def fake_text(value: Any) -> str:
    return f"'{fake.text()}'"


def fake_password(value: Any) -> str:
    return f"'{fake.password(length=16)}'"


def fake_phone_number(value: Any) -> str:
    return f"'{fake.phone_number()}'"


def fake_address(value: Any) -> str:
    return f"'{fake.address()}'"


def fake_image_url(value: Any) -> str:
    return f"'{fake.image_url()}'"


def nullify(value: Any) -> str:
    return "NULL"


def get_strategies() -> dict[str, Callable[[Any], str]]:
    return {
        "fake_username": fake_username,
        "fake_fullname": fake_fullname,
        "fake_text": fake_text,
        "fake_email": fake_email,
        "fake_password": fake_password,
        "fake_phone_number": fake_phone_number,
        "fake_address": fake_address,
        "nullify": nullify,
    }
