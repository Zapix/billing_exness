# -*- coding: utf-8 -*-
from django_filters import rest_framework as filters

from billing_exness.billing.models import Transaction


class TransactionFilter(filters.FilterSet):
    before = filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte'
    )
    after = filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte'
    )

    class Meta:
        model = Transaction
        fields = ['before', 'after']
