# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest

from ..constants import USD, CAD, EUR, CNY
from ..utils import charge, make_payment, get_wallet
from billing_exness.billing.exceptions import NotEnoughMoneyException
from .factories import WalletFactory, ExchangeRateFactory
from billing_exness.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestGetWallet:

    def test_wallet_to_wallet(self):
        wallet = WalletFactory.create()

        assert wallet.pk == get_wallet(wallet).pk

    def test_user_without_wallet(self):
        user = UserFactory.create()

        with pytest.raises(ValueError):
            get_wallet(user)

    def test_user_to_wallet(self):
        wallet = WalletFactory.create()
        user = wallet.user

        assert wallet.pk == get_wallet(user).pk


class TestCharge:

    def test_charge_wrong_currency(self):
        wallet = WalletFactory.create()
        with pytest.raises(AssertionError):
            charge(wallet, Decimal("100.0"), 'RUR')

    def test_charge_negative_amount(self):
        wallet = WalletFactory.create(
            currency=USD
        )
        with pytest.raises(AssertionError):
            charge(wallet, Decimal("-10"), USD)

    def test_charge_user_without_wallet(self):
        user = UserFactory.create()
        with pytest.raises(ValueError):
            charge(user, Decimal("100.0"), USD)

    def test_charge_wallet_with_same_currency(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        wallet = WalletFactory(
            amount=Decimal("100.0"),
            currency=EUR
        )
        updated_wallet = charge(wallet, Decimal("50"), EUR)
        assert updated_wallet.amount == Decimal("150")

        transaction = updated_wallet.transactions.first()
        assert transaction.amount == Decimal("50")
        assert transaction.currency == EUR

    def test_charge_wallet_with_cad_by_eur(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        ExchangeRateFactory.create(
            rate=Decimal("4"),
            currency=CAD
        )
        wallet = WalletFactory(
            amount=Decimal("100.0"),
            currency=EUR
        )
        updated_wallet = charge(wallet, Decimal("50"), CAD)
        assert updated_wallet.amount == Decimal("125")


class TestMakePayment:

    def test_not_enough_money_same_currency(self):
        from_wallet = WalletFactory.create(
            amount=Decimal(10),
            currency=USD,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal(1),
            currency=USD
        )

        with pytest.raises(NotEnoughMoneyException):
            make_payment(
                from_wallet,
                to_wallet,
                Decimal("100"),
                USD
            )

    def test_not_enough_money_different_currency(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        ExchangeRateFactory.create(
            rate=Decimal("4"),
            currency=CAD
        )

        from_wallet = WalletFactory.create(
            amount=Decimal(10),
            currency=EUR,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal(1),
            currency=USD
        )

        with pytest.raises(NotEnoughMoneyException):
            make_payment(
                from_wallet,
                to_wallet,
                Decimal("100"),
                CAD
            )

    def test_same_currencies(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=EUR,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=EUR
        )

        transaction = make_payment(from_wallet, to_wallet, Decimal("4"), EUR)

        assert transaction.amount == Decimal("4")
        assert transaction.currency == EUR

        from_wallet.refresh_from_db()
        assert from_wallet.amount == Decimal("6")
        assert from_wallet.currency == EUR

        to_wallet.refresh_from_db()
        assert to_wallet.amount == Decimal("5")
        assert to_wallet.currency == EUR

    def test_from_wallet_same_currency(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=USD,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=EUR
        )

        transaction = make_payment(from_wallet, to_wallet, Decimal("3"), USD)

        assert transaction.amount == Decimal("3")
        assert transaction.currency == USD

        from_wallet.refresh_from_db()
        assert from_wallet.amount == Decimal("7")
        assert from_wallet.currency == USD

        assert to_wallet.amount == Decimal("7")
        assert to_wallet.currency == EUR

    def test_to_wallet_same_currency(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=USD,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=EUR
        )

        transaction = make_payment(from_wallet, to_wallet, Decimal("3"), EUR)

        assert transaction.amount == Decimal("3")
        assert transaction.currency == EUR

        from_wallet.refresh_from_db()
        assert from_wallet.amount == Decimal("8.5")
        assert from_wallet.currency == USD

        to_wallet.refresh_from_db()
        assert to_wallet.amount == Decimal("4")
        assert to_wallet.currency == EUR

    def test_all_different_currencies(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        ExchangeRateFactory.create(
            rate=Decimal("4"),
            currency=CAD
        )
        ExchangeRateFactory.create(
            rate=Decimal("6"),
            currency=CNY
        )

        from_wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=EUR,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=CAD
        )

        transaction = make_payment(from_wallet, to_wallet, Decimal("6"), CNY)

        assert transaction.amount == Decimal("6")
        assert transaction.currency == CNY

        from_wallet.refresh_from_db()
        assert from_wallet.amount == Decimal("8")
        assert from_wallet.currency == EUR

        to_wallet.refresh_from_db()
        assert to_wallet.amount == Decimal("5")
        assert to_wallet.currency == CAD

    def test_negative_amount(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=EUR,
        )
        to_wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=EUR
        )

        with pytest.raises(AssertionError):
            make_payment(from_wallet, to_wallet, Decimal("-4"), EUR)
