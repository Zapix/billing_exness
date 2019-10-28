# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest

from ..serializers import ExchangeRateSerializer
from billing_exness.billing.models import ExchangeRate
from billing_exness.billing.constants import EUR, CAD
from billing_exness.billing.tests.factories import ExchangeRateFactory

pytestmark = pytest.mark.django_db


class TestExchangeRateSerializer:

    def test_exchange_save_success(self):
        serializer = ExchangeRateSerializer(
            currency=EUR,
            data={
                'rate': Decimal("2")
            }
        )

        assert serializer.is_valid()

        rate = serializer.save()

        assert rate.rate == Decimal("2")
        assert rate.currency == EUR

    def test_exchange_update_new_value(self):
        old_rate = ExchangeRateFactory.create(
            rate=Decimal("1.5"),
            currency=EUR
        )

        serializer = ExchangeRateSerializer(
            instance=old_rate,
            data={
                'rate': Decimal("2")
            },
            currency=EUR
        )

        assert serializer.is_valid()

        rate = serializer.save()
        assert rate.currency == old_rate.currency
        assert rate.pk != old_rate.pk
        assert ExchangeRate.of(EUR) == rate.rate

    def test_exchange_wrong_currency_passed(self):
        with pytest.raises(AssertionError):
            ExchangeRateSerializer(
                data={'rate': Decimal("63")},
                currency='RUR'
            )

    def test_exchange_update_different_currencies(self):
        old_rate = ExchangeRateFactory.create(
            rate=Decimal("1.5"),
            currency=EUR
        )

        with pytest.raises(AssertionError):
            ExchangeRateSerializer(
                old_rate,
                data={'rate': Decimal("63")},
                currency=CAD
            )
