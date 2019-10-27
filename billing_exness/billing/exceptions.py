# -*- coding: utf-8 -*-
from .constants import CURRENCIES


class NotEnoughMoneyException(Exception):
    """
    Raise exception when user hasn't got enough money to make payment
    """
    pass


def check_currency(currency: str):
    """
    Checks that currency is available for us
    """
    assert currency in CURRENCIES
