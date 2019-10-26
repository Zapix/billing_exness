# -*- coding: utf-8 -*-

from factory import fuzzy, DjangoModelFactory, SubFactory

from billing_exness.users.tests.factories import UserFactory
from ..constants import CURRENCIES, EXCHANGE_CURRENCIES
from ..models import (
    ExchangeRate,
    Wallet,
    Transaction
)


class ExchangeRateFactory(DjangoModelFactory):
    rate = fuzzy.FuzzyDecimal(low=0.1, high=100)
    currency = fuzzy.FuzzyChoice(EXCHANGE_CURRENCIES)

    class Meta:
        model = ExchangeRate


class WalletFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)

    amount = fuzzy.FuzzyDecimal(low=0.1, high=1000000)
    currency = fuzzy.FuzzyChoice(CURRENCIES)

    class Meta:
        model = Wallet


class TransactionFactory(DjangoModelFactory):
    from_wallet = SubFactory(WalletFactory)
    to_wallet = SubFactory(WalletFactory)

    amount = fuzzy.FuzzyDecimal(low=0.1, high=1000000)
    currency = fuzzy.FuzzyChoice(CURRENCIES)

    class Meta:
        model = Transaction
