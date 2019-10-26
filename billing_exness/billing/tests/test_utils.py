# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest

from ..constants import USD, CAD, EUR
from ..utils import charge
from .factories import WalletFactory, ExchangeRateFactory
from billing_exness.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCharge:

    def test_charge_wrong_currency(self):
        wallet = WalletFactory.create()
        with pytest.raises(AssertionError):
            charge(wallet, Decimal("100.0"), 'RUR')

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
