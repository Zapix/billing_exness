# -*- coding: utf-8 -*-
from typing import Optional

from django.http import Http404
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from billing_exness.billing.constants import EUR
from billing_exness.billing.models import ExchangeRate
from billing_exness.openapi.schema import SecurityRequiredSchema
from .serializers import ExchangeRateSerializer


class ExchangeRateApiView(generics.RetrieveUpdateAPIView):
    """
    Retrieves info about rate of currency
    """
    serializer_class = ExchangeRateSerializer
    update_permission_classes = [permissions.IsAdminUser]
    schema = SecurityRequiredSchema()

    def get_permissions(self):
        if self.request.method == 'GET':
            return super().get_permissions()
        return [permission() for permission in self.update_permission_classes]

    def get_serializer(self, *args, **kwargs) -> ExchangeRateSerializer:
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        # set default ad EUR to support schema generation
        kwargs['currency'] = self.kwargs.get('currency', EUR)

        return serializer_class(*args, **kwargs)

    def get_object(self) -> Optional[ExchangeRate]:
        currency: str = self.kwargs['currency'].upper()
        try:
            rate = ExchangeRate.of(currency, as_object=True)
        except ValueError:
            return None
        except AssertionError:
            raise Http404()
        else:
            assert isinstance(rate, ExchangeRate)
            return rate

    def patch(self, request, *args, **kwargs) -> Response:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
