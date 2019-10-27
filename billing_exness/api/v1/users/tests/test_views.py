# -*- coding: utf-8 -*-
import pytest
from django.shortcuts import reverse
from rest_framework.test import APIClient

from billing_exness.billing.constants import EUR
from billing_exness.users.tests.factories import UserFactory
from billing_exness.billing.tests.factories import WalletFactory
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
