# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest

from billing_exness.users.tests.factories import UserFactory
from billing_exness.billing.tests.factories import (
    WalletFactory,
    ExchangeRateFactory
)
from billing_exness.billing.constants import EUR, USD
from ..serializers import (
    CreateUserSerializer,
    ChargeSerializer,
    PaymentSerializer
)

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


class TestPaymentSerializer:

    def test_make_payment_to_user_wihtout_wallet(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        from_user = wallet.user
        to_user = UserFactory.create()

        serializer = PaymentSerializer(
            data={
                'to_user': to_user.get_username(),
                'amount': Decimal('10'),
                'currency': EUR
            }
        )

        assert serializer.is_valid()
        with pytest.raises(ValueError):
            serializer.save(from_user)

    def test_make_payment_from_user_without_wallet(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_user = UserFactory.create()
        wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        to_user = wallet.user

        serializer = PaymentSerializer(
            data={
                'to_user': to_user.get_username(),
                'amount': Decimal('10'),
                'currency': EUR
            }
        )

        assert serializer.is_valid()
        with pytest.raises(ValueError):
            serializer.save(from_user)

    def test_make_payment_success(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("60"),
            currency=EUR
        )
        from_user = from_wallet.user

        to_wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        to_user = to_wallet.user

        serializer = PaymentSerializer(
            data={
                'to_user': to_user.get_username(),
                'amount': Decimal('10'),
                'currency': EUR
            }
        )

        assert serializer.is_valid()
        transaction = serializer.save(from_user)

        assert transaction.pk is not None
        assert transaction.amount == Decimal('10')
        assert transaction.currency == EUR
        assert transaction.from_wallet.pk == from_wallet.pk
        assert transaction.to_wallet.pk == to_wallet.pk
