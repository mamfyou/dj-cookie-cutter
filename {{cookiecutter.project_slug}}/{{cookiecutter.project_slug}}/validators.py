import re

from py_code_meli import is_valid_code_meli
from rest_framework.serializers import ValidationError


def is_valid_iranian_mobile(value):
    pattern = r'^09[0-9]{9}$'
    if not re.match(pattern, value):
        raise ValidationError('شماره همراه وارد شده معتبر نمی باشد!')


def validate_iranian_national_code(value):
    if not is_valid_code_meli(value):
        raise ValidationError('کد ملی نامعتبر می باشد!')
