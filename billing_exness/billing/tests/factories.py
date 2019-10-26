# -*- coding: utf-8 -*-

from factory import fuzzy, DjangoModelFactory

from billing_exness.billing.constants import EXCHANGE_CURRENCIES
from billing_exness.billing.models import ExchangeRate


class ExchangeRateFactory(DjangoModelFactory):
    rate = fuzzy.FuzzyDecimal(low=0.1, high=100)
    currency = fuzzy.FuzzyChoice(EXCHANGE_CURRENCIES)

    class Meta:
        model = ExchangeRate
