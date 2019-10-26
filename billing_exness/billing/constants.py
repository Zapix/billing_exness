# -*- coding: utf-8 -*-
USD = 'USD'
EUR = 'EUR'
CAD = 'CAD'
CNY = 'CNY'

BASE_CURRENCY = USD

CURRENCIES = [USD, EUR, CAD, CNY]

EXCHANGE_CURRENCIES = [
    currency
    for currency in CURRENCIES
    if currency != BASE_CURRENCY
]
