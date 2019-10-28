# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from django.shortcuts import reverse
from rest_framework.test import APIClient

from billing_exness.billing.constants import USD, EUR
from billing_exness.billing.tests.factories import ExchangeRateFactory
from billing_exness.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestExhangeRateApiView:

    def test_exchange_rate_not_found(self):
        client = APIClient()
        response = client.get(reverse(
            'api_v1:exchange:rate',
            kwargs={'currency': 'RUR'},
        ))
        assert response.status_code == 404

    def test_400_for_uds_rate(self):
        client = APIClient()
        response = client.get(reverse(
            'api_v1:exchange:rate',
            kwargs={'currency': USD}
        ))
        assert response.status_code == 404

    def test_exchange_rate_does_not_set(self):
        client = APIClient()
        response = client.get(reverse(
            'api_v1:exchange:rate',
            kwargs={'currency': EUR}
        ))
        assert response.status_code == 200

    def test_exchange_rate_success(self):
        ExchangeRateFactory.create(
            rate=Decimal('2.2'),
            currency=EUR
        )

        client = APIClient()
        response = client.get(reverse(
            'api_v1:exchange:rate',
            kwargs={'currency': EUR}
        ))

        assert response.status_code == 200
        for field in ['rate', 'created']:
            assert field in response.data

    def test_exchange_rate_update_no_permission(self):
        user = UserFactory.create()
        client = APIClient()
        client.force_login(user)

        response = client.put(
            reverse('api_v1:exchange:rate', kwargs={'currency': EUR}),
            data={
                "rate": 2
            }
        )
        assert response.status_code == 403

    def test_exchange_rate_update_success(self):
        user = UserFactory.create()
        user.is_superuser = True
        user.is_staff = True
        user.save()
        client = APIClient()
        client.force_login(user)

        response = client.put(
            reverse('api_v1:exchange:rate', kwargs={'currency': EUR}),
            data={
                "rate": '2.00'
            }
        )
        assert response.status_code == 200
        assert response.data['rate'] == '2.00'

    def test_exchange_rate_patch_method_not_allowed(self):
        user = UserFactory.create()
        user.is_superuser = True
        user.is_staff = True
        user.save()
        client = APIClient()
        client.force_login(user)

        response = client.patch(
            reverse('api_v1:exchange:rate', kwargs={'currency': EUR}),
            data={
                'rate': 3
            }
        )
        assert response.status_code == 405
