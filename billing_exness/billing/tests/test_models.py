# -*- coding: utf-8 -*-
import pytest
from decimal import Decimal

from .factories import ExchangeRateFactory, WalletFactory
from ..models import ExchangeRate
from ..constants import USD, CAD, EUR

pytestmark = pytest.mark.django_db


def test_exchange_of_usd():
    assert ExchangeRate.of(USD) == Decimal("1")


def test_exchange_wrong_currency():
    with pytest.raises(AssertionError):
        ExchangeRate.of('RUR')


def test_exchange_rate_not_set():
    with pytest.raises(ValueError):
        ExchangeRate.of(CAD)


def test_exchange_rate_set():
    ExchangeRateFactory.create(
        rate=Decimal(1.1),
        currency=CAD
    )

    assert ExchangeRate.of(CAD) == Decimal("1.1")


def test_exchange_rate_set_several_times():
    ExchangeRateFactory.create_batch(
        10,
        currency=CAD
    )

    latest = ExchangeRateFactory.create(
        currency=CAD
    )

    assert ExchangeRate.of(CAD) == latest.rate


def test_get_usd_to_cad():
    ExchangeRateFactory.create(rate=Decimal("1.5"), currency=CAD)
    assert ExchangeRate.get(USD, CAD) == Decimal("1.5")


def test_get_cad_to_usd():
    ExchangeRateFactory.create(rate=Decimal("1.5"), currency=CAD)
    assert ExchangeRate.get(CAD, USD) == Decimal("2") / Decimal("3")


def test_get_cad_to_eur():
    ExchangeRateFactory.create(rate=Decimal("2"), currency=CAD)
    ExchangeRateFactory.create(rate=Decimal("3"), currency=EUR)

    assert ExchangeRate.get(CAD, EUR) == Decimal("1.5")


@pytest.mark.watch
def test_amount_usd_in_usd():
    wallet = WalletFactory.create(currency=USD)
    assert wallet.amount == wallet.amount_in(USD)


@pytest.mark.watch
def test_amount_eur_in_eur():
    wallet = WalletFactory.create(currency=EUR)
    ExchangeRateFactory.create(
        rate=Decimal("2"),
        currency=EUR
    )
    assert wallet.amount == wallet.amount_in(EUR)


@pytest.mark.watch
def test_amount_usd_in_eur():
    wallet = WalletFactory.create(
        amount=Decimal("100"),
        currency=USD
    )
    ExchangeRateFactory.create(
        rate=Decimal("2"),
        currency=EUR
    )

    assert wallet.amount_in(EUR) == Decimal("200")


@pytest.mark.watch
def test_amount_eur_in_usd():
    wallet = WalletFactory.create(
        amount=Decimal("100"),
        currency=EUR,
    )
    ExchangeRateFactory.create(
        rate=Decimal("2"),
        currency=EUR
    )

    assert wallet.amount_in(USD) == Decimal("50")


@pytest.mark.watch
def test_amount_eur_in_cad():
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
