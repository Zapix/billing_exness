# -*- coding: utf-8 -*-
from typing import Union
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction

from .models import Wallet, ExchangeRate, Transaction
from .exceptions import NotEnoughMoneyException, check_currency

User = get_user_model()


def get_wallet(wallet: Union[AbstractBaseUser, Wallet]) -> Wallet:
    """
    Checks has user wallet.
    Raises:
        ValueError if user hasn`t got wallet
    """
    if isinstance(wallet, User):
        try:
            wallet = wallet.wallet
        except Wallet.DoesNotExist:
            raise ValueError(f"User {wallet.get_username()} hasn`t got wallet")
    assert isinstance(wallet, Wallet)

    return wallet


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
    check_currency(currency)

    wallet = get_wallet(wallet)

    rate = ExchangeRate.get(currency, wallet.currency)
    wallet.amount += amount * rate
    wallet.save()

    return wallet


@transaction.atomic
def make_payment(
    from_wallet: Union[AbstractBaseUser, Wallet],
    to_wallet: Union[AbstractBaseUser, Wallet],
    amount: Decimal,
    currency: str
) -> Transaction:
    """
    Make payment from `from_wallet` to `to_wallet` in any currencies.
    Checks that from_wallet has got enough money for processing it.
    Stores info about transaction in db
    Params:
        from_wallet - `Wallet` or `User` that will pay
        to_wallet - `Wallet` or `User` that will receive payment
        amount - amount of payment in Decial
        currency - currency of processing payment
    Raises:
        AssertionError - if wrong currency has been passed
        ValueError - if one of passed users hasn`t got wallet
        NotEnoughMoneyException - if from_wallet hasn`t got enough money to
                                  proceed transaction
    Returns:
        `Transaction` - object of current transaction
    """
    check_currency(currency)

    from_wallet = get_wallet(from_wallet)
    to_wallet = get_wallet(to_wallet)

    from_rate = ExchangeRate.get(from_wallet.currency, currency)
    to_rate = ExchangeRate.get(currency, to_wallet.currency)

    if from_rate * from_wallet.amount < amount:
        username = from_wallet.user.get_username()
        raise NotEnoughMoneyException(
            f"{username} hasn`t got {amount} {currency}"
        )

    from_wallet.amount -= amount / from_rate
    to_wallet.amount += amount * to_rate

    from_wallet.save()
    to_wallet.save()

    return Transaction.objects.create(
        from_wallet=from_wallet,
        to_wallet=to_wallet,
        amount=amount,
        currency=currency
    )
