# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest

from billing_exness.users.tests.factories import UserFactory
from billing_exness.billing.tests.factories import (
    WalletFactory,
    ExchangeRateFactory
)
from billing_exness.billing.constants import EUR, USD
from ..serializers import CreateUserSerializer, ChargeSerializer

pytestmark = pytest.mark.django_db


class TestCreateUserSerializer:

    def test_required_fields(self):
        serializer = CreateUserSerializer(data={})

        assert not serializer.is_valid()
        for field in ['username', 'currency', 'password1']:
            assert field in serializer.errors

    def test_username_has_been_registerd_before(self):
        user = UserFactory.create()
        serializer = CreateUserSerializer(
            data={
                'username': user.get_username()
            }
        )
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_password_do_not_match(self):
        serializer = CreateUserSerializer(
            data={
                'username': 'veryuniquename',
                'currency': EUR,
                'password1': 'v3ry$r0ngp4ssvvrd',
                'password2': 'wrongpass'
            }
        )

        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors, serializer.errors

    def test_save_success(self):
        serializer = CreateUserSerializer(
            data={
                'username': 'veryuniquename',
                'currency': EUR,
                'password1': 'v3ry$r0ngp4ssvvrd',
                'password2': 'v3ry$r0ngp4ssvvrd',
            }
        )

        assert serializer.is_valid()

        user = serializer.save()

        assert user.get_username() == 'veryuniquename'
        assert user.wallet.currency == EUR


class TestChargeSerializer:

    def test_serializer_save(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )

        wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=EUR
        )
        serializer = ChargeSerializer(data={
            'amount': Decimal("10"),
            'currency': USD
        })

        assert serializer.is_valid()
        serializer.save(wallet)

        wallet.refresh_from_db()

        assert wallet.amount == Decimal("21")
        assert wallet.currency == EUR
