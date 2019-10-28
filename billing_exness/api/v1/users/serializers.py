# -*- coding: utf-8 -*-
from typing import Callable
from rest_framework import serializers
from decimal import Decimal

from django.conf import settings
from django.utils.module_loading import import_string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MinValueValidator

from billing_exness.billing.constants import CURRENCIES
from billing_exness.billing.models import Wallet, Transaction
from billing_exness.billing.utils import charge, make_payment

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


class ChargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        validators=[
            MinValueValidator(0)
        ]
    )
    currency = serializers.ChoiceField(
        choices=CURRENCIES,
        required=True
    )

    def save(self, wallet: Wallet):
        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        charge(
            wallet,
            self.validated_data['amount'],
            self.validated_data['currency']
        )


class PaymentSerializer(serializers.Serializer):
    """
    Allow make payment to user
    """

    to_user = serializers.ModelField(
        model_field=User()._meta.get_field('username')
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        validators=[
            MinValueValidator(0)
        ],
    )
    currency = serializers.ChoiceField(
        choices=CURRENCIES,
        required=True
    )

    def save(self, from_user: AbstractBaseUser) -> Transaction:
        """
        Makes payment from user
        """
        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        return make_payment(
            from_user,
            User.objects.get(username=self.validated_data['to_user']),
            self.validated_data['amount'],
            self.validated_data['currency']
        )


class TransactionSerializer(serializers.ModelSerializer):
    to_username = serializers.CharField(
        source='to_wallet.user.username'
    )
    from_username = serializers.CharField(
        source='from_wallet.user.username'
    )

    class Meta:
        model = Transaction
        fields = ['to_username', 'amount', 'currency', 'from_username']
        read_only_fields = [
            'to_username',
            'amount',
            'currency',
            'from_username'
        ]
