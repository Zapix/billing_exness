# -*- coding: utf-8 -*-
from typing import Callable
from rest_framework import serializers
from decimal import Decimal

from django.conf import settings
from django.utils.module_loading import import_string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

from billing_exness.billing.constants import CURRENCIES
from billing_exness.billing.models import Wallet

User = get_user_model()


def get_password_validator(validator_path: str) -> Callable:
    return lambda x: import_string(validator_path)().validate(password=x)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'city',
            'country'
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        required=True,
        validators=[
            get_password_validator(validator['NAME'])
            for validator in settings.AUTH_PASSWORD_VALIDATORS
        ]
    )
    password2 = serializers.CharField()
    currency = serializers.ChoiceField(
        choices=CURRENCIES,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'city',
            'country',
            'currency',
            'password1',
            'password2'
        ]

    def validate(self, attrs: dict) -> dict:
        """
        Checks that password1 matches password2
        """
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def save(self) -> AbstractBaseUser:
        user = User.objects.create(
            username=self.validated_data['username'],
            name=self.validated_data.get('name', ''),
            city=self.validated_data.get('city', ''),
            country=self.validated_data.get('country', ''),
        )
        user.set_password(self.validated_data['password1'])

        wallet = Wallet.objects.create(
            user=user,
            amount=Decimal("0"),
            currency=self.validated_data['currency']
        )
        user.wallet = wallet
        user.save()

        return user


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ['amount', 'currency']
