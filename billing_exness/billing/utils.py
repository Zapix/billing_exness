# -*- coding: utf-8 -*-
from typing import Union
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db  import transaction

from .models import Wallet, ExchangeRate
from .constants import CURRENCIES

User = get_user_model()


@transaction.atomic
def charge(
    wallet: Union[AbstractBaseUser, Wallet],
    amount: Decimal,
    currency: str,
) -> Wallet:
    """
    Charges users wallet from outer world. And add transaction for
    current operation.
    Params:
        wallet - wallet that should be charged or users entity which wallet
                 should be charged
        amount - amount that should be charged
        currency - currency of amount
    Raises:
        AssertionError - if wrong currency has been passed
        ValueError - if user hasn`t got wallet
    Returns:
        `Wallet` - updated wallet
    """
    assert currency in CURRENCIES

    if isinstance(wallet, User):
        try:
            wallet = wallet.wallet
        except Wallet.DoesNotExist:
            raise ValueError(f"User {wallet.get_username()} hasn`t got wallet")

    assert isinstance(wallet, Wallet)

    rate = ExchangeRate.get(currency, wallet.currency)
    wallet.amount += amount * rate
    wallet.save()

    return wallet
