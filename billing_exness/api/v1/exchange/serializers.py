# -*- coding: utf-8 -*-
from rest_framework import serializers

from billing_exness.billing.models import ExchangeRate
from billing_exness.billing.exceptions import check_currency


class ExchangeRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExchangeRate
        fields = ['rate', 'created']
        read_only_fields = ['created']

    def __init__(
        self,
        instance: ExchangeRate = None,
        currency: str = None,
        **kwargs
    ):
        check_currency(currency)

        if instance is not None:
            assert instance.currency == currency

        self.currency = currency
        super().__init__(instance=instance, **kwargs)

    def save(self, **kwargs):
        self.instance = ExchangeRate.objects.create(
            rate=self.validated_data['rate'],
            currency=self.currency
        )
        return self.instance
