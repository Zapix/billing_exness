# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from django.db.models import QuerySet

from .factories import ExchangeRateFactory, WalletFactory, TransactionFactory
from ..models import ExchangeRate
from ..constants import USD, CAD, EUR

pytestmark = pytest.mark.django_db


class TestExchangeRate:
    def test_exchange_of_usd(self):
        assert ExchangeRate.of(USD) == Decimal("1")

    def test_exchange_wrong_currency(self):
        with pytest.raises(AssertionError):
            ExchangeRate.of('RUR')

    def test_exchange_rate_not_set(self):
        with pytest.raises(ValueError):
            ExchangeRate.of(CAD)

    def test_exchange_rate_set(self):
        ExchangeRateFactory.create(
            rate=Decimal(1.1),
            currency=CAD
        )

        assert ExchangeRate.of(CAD) == Decimal("1.1")

    def test_exchange_rate_set_several_times(self):
        ExchangeRateFactory.create_batch(
            10,
            currency=CAD
        )

        latest = ExchangeRateFactory.create(
            currency=CAD
        )

        assert ExchangeRate.of(CAD) == latest.rate


class TestWallet:

    def test_get_usd_to_cad(self):
        ExchangeRateFactory.create(rate=Decimal("1.5"), currency=CAD)
        assert ExchangeRate.get(USD, CAD) == Decimal("1.5")

    def test_get_cad_to_usd(self):
        ExchangeRateFactory.create(rate=Decimal("1.5"), currency=CAD)
        assert ExchangeRate.get(CAD, USD) == Decimal("2") / Decimal("3")

    def test_get_cad_to_eur(self):
        ExchangeRateFactory.create(rate=Decimal("2"), currency=CAD)
        ExchangeRateFactory.create(rate=Decimal("3"), currency=EUR)

        assert ExchangeRate.get(CAD, EUR) == Decimal("1.5")

    def test_amount_usd_in_usd(self):
        wallet = WalletFactory.create(currency=USD)
        assert wallet.amount == wallet.amount_in(USD)

    def test_amount_eur_in_eur(self):
        wallet = WalletFactory.create(currency=EUR)
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        assert wallet.amount == wallet.amount_in(EUR)

    def test_amount_usd_in_eur(self):
        wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=USD
        )
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )

        assert wallet.amount_in(EUR) == Decimal("200")

    def test_amount_eur_in_usd(self):
        wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR,
        )
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )

        assert wallet.amount_in(USD) == Decimal("50")

    def test_amount_eur_in_cad(self):
        wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR,
        )
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        ExchangeRateFactory.create(
            rate=Decimal("4"),
            currency=CAD
        )

        assert wallet.amount_in(CAD) == Decimal("200")

    def test_transactions_hasnt_been_prefetched(self):
        first_wallet = WalletFactory.create()
        second_wallet = WalletFactory.create()

        TransactionFactory.create_batch(
            15,
            from_wallet=first_wallet,
            to_wallet=second_wallet,
        )
        TransactionFactory.create_batch(
            5,
            from_wallet=second_wallet,
            to_wallet=first_wallet
        )
        TransactionFactory.create_batch(
            4,
            to_wallet=first_wallet
        )

        assert isinstance(first_wallet.transactions, QuerySet)
        assert first_wallet.transactions.count() == 24
