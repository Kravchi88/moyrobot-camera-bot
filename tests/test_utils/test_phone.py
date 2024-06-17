import pytest

from app.utils.phone import is_phone_correct, phone_to_text


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("+79092330123", True),
        ("89092930333", True),
        ("34123123123", False),
        ("+89092230431", False),
        ("79092320123", True),
        ("@asd123123l", False),
    ],
)
def test_phone_is_correct(test_input, expected):
    assert is_phone_correct(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("+79092330123", "+79092330123"),
        ("+7(903)12-23-33", "+7903122333"),
        ("+7903)12-23-33", "+7903122333"),
        ("+7(90312-----23-33", "+7903122333"),
        ("+7(90312-2333", "+7903122333"),
    ],
)
def test_phone_to_text(test_input, expected):
    assert phone_to_text(test_input) == expected
