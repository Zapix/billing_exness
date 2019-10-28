# -*- coding: utf-8 -*-
from django.shortcuts import Http404

from django.contrib.auth.models import AbstractBaseUser
from rest_framework import generics
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from billing_exness.openapi.schema import SecurityRequiredSchema
from billing_exness.billing.models import Wallet, Transaction
from billing_exness.billing.exceptions import NotEnoughMoneyException
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    WalletSerializer,
    ChargeSerializer,
    PaymentSerializer,
    TransactionSerializer
)


class CreateUserApiView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer) -> AbstractBaseUser:
        return serializer.save()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class UserMeApiView(generics.RetrieveAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    schema = SecurityRequiredSchema()

    def get_object(self):
        return self.request.user


class WalletApiView(generics.RetrieveUpdateAPIView):

    serializer_class = WalletSerializer
    charge_serializer_class = ChargeSerializer
    permission_classes = [IsAuthenticated]
    schema = SecurityRequiredSchema()

    def get_object(self):
        try:
            return self.request.user.wallet
        except Wallet.DoesNotExist:
            raise Http404()

    def get_serializer(self, instance=None, data=None, **kwargs):
        """
        Uses ChargeSerializer if update data passes
        """
        if data is None:
            return super().get_serializer(instance, **kwargs)
        return self.charge_serializer_class(data=data, **kwargs)

    def perform_update(self, serializer):
        """
        Charges users wallet
        """
        wallet = self.get_object()
        serializer.save(wallet)

    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
        except ValueError as e:
            return Response(
                data={api_settings.NON_FIELD_ERRORS_KEY: str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        wallet = self.get_object()
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PaymentApiView(generics.CreateAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [
        IsAuthenticated
    ]
    schema = SecurityRequiredSchema()

    def perform_create(self, serializer: PaymentSerializer) -> Transaction:
        return serializer.save(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transaction = self.perform_create(serializer)
        except (ValueError, NotEnoughMoneyException) as e:
            return Response(
                {api_settings.NON_FIELD_ERRORS_KEY: str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            transaction_serializer = TransactionSerializer(transaction)
            headers = self.get_success_headers(transaction_serializer.data)
            return Response(
                transaction_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
