# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from django.shortcuts import reverse
from rest_framework.test import APIClient
from rest_framework.settings import api_settings

from billing_exness.billing.constants import EUR, CAD
from billing_exness.users.tests.factories import UserFactory
from billing_exness.billing.tests.factories import (
    WalletFactory,
    ExchangeRateFactory
)
pytestmark = pytest.mark.django_db


class TestCreateUserApi:

    def test_create_error(self):
        client = APIClient()
        response = client.post(
            reverse('api_v1:users:create'),
            {
                'username': 'fake',
                'password1': '1',
                'password2': '2'
            },
            format='json'
        )
        assert response.status_code == 400

    def test_create_success(self):
        client = APIClient()
        response = client.post(
            reverse('api_v1:users:create'),
            {
                'username': 'veryuniquename',
                'currency': EUR,
                'password1': 'v3ry$r0ngp4ssvvrd',
                'password2': 'v3ry$r0ngp4ssvvrd',
            },
            format='json'
        )
        assert response.status_code == 201
        assert response.data['username'] == 'veryuniquename'
        assert 'password1' not in response.data
        assert 'password2' not in response.data
        assert 'currency' not in response.data


class TestGetUserInfo:

    def test_permission_denied(self):
        client = APIClient()
        response = client.get(reverse('api_v1:users:me'))

        assert response.status_code == 401

    def test_permission_succeeded(self):
        user = UserFactory.create()
        client = APIClient()
        client.force_login(user)

        response = client.get(reverse('api_v1:users:me'))

        assert response.status_code == 200


class TestUsersWallet:

    def test_permission_denied(self):
        client = APIClient()
        response = client.get(reverse('api_v1:users:wallet'))

        assert response.status_code == 401

    def test_permission_without_wallet(self):
        user = UserFactory.create()
        client = APIClient()
        client.force_login(user)

        response = client.get(reverse('api_v1:users:wallet'))

        assert response.status_code == 404

    def test_user_with_wallet(self):
        wallet = WalletFactory.create()
        user = wallet.user
        client = APIClient()
        client.force_login(user)

        response = client.get(reverse('api_v1:users:wallet'))

        assert response.status_code == 200

    def test_wallet_charge_success(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        ExchangeRateFactory.create(
            rate=Decimal("4"),
            currency=CAD
        )
        wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=EUR
        )
        user = wallet.user

        client = APIClient()
        client.force_login(user)

        response = client.put(
            reverse('api_v1:users:wallet'),
            {
                'amount': 2,
                'currency': CAD,
            }
        )
        assert response.status_code == 200
        assert response.data['amount'] == "11.00"
        assert response.data['currency'] == EUR

    def test_wallet_chrage_no_rate(self):
        wallet = WalletFactory.create(
            amount=Decimal("10"),
            currency=EUR
        )
        user = wallet.user

        client = APIClient()
        client.force_login(user)

        response = client.put(
            reverse('api_v1:users:wallet'),
            {
                'amount': 2,
                'currency': CAD,
            }
        )
        assert response.status_code == 400


class TestPaymentApiView:

    def test_payment_user_without_wallet(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_user = UserFactory.create()

        to_wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        to_user = to_wallet.user

        client = APIClient()
        client.force_login(from_user)
        response = client.post(
            reverse('api_v1:users:payment'),
            {
                'to_user': to_user.get_username(),
                'amount': 5,
                'currency': EUR,
            }
        )

        assert response.status_code == 400
        assert api_settings.NON_FIELD_ERRORS_KEY in response.data

    def test_payment_not_enough_money(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("1"),
            currency=EUR
        )
        from_user = from_wallet.user

        to_wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        to_user = to_wallet.user

        client = APIClient()
        client.force_login(from_user)
        response = client.post(
            reverse('api_v1:users:payment'),
            {
                'to_user': to_user.get_username(),
                'amount': 5,
                'currency': EUR,
            }
        )

        assert response.status_code == 400
        assert api_settings.NON_FIELD_ERRORS_KEY in response.data

    def test_payment_success(self):
        ExchangeRateFactory.create(
            rate=Decimal("2"),
            currency=EUR
        )
        from_wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        from_user = from_wallet.user

        to_wallet = WalletFactory.create(
            amount=Decimal("100"),
            currency=EUR
        )
        to_user = to_wallet.user

        client = APIClient()
        client.force_login(from_user)
        response = client.post(
            reverse('api_v1:users:payment'),
            {
                'to_user': to_user.get_username(),
                'amount': 5,
                'currency': EUR,
            }
        )

        assert response.status_code == 201

        fields = [
            'to_user',
            'amount',
            'currency',
            'from_user',
            'created'
        ]

        for field in fields:
            assert field in response.data
