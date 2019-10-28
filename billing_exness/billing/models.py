from typing import Union
from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from model_utils import Choices
from model_utils.models import TimeStampedModel
from model_utils.fields import StatusField

# Create your models here.
from .constants import (
    BASE_CURRENCY,
    EXCHANGE_CURRENCIES,
    CURRENCIES
)
from .exceptions import check_currency


class ExchangeRate(TimeStampedModel):
    """
    Store information about exchange rate between
    billing default currency(USD) and other.
    1(USD) cost `rate`(`currency`)
    """
    EXCHANGE_CURRENCIES = Choices(*EXCHANGE_CURRENCIES)

    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    currency = StatusField(
        choices_name='EXCHANGE_CURRENCIES',
        db_index=True
    )

    class Meta:
        ordering = ('-created', )

    @classmethod
    def of(
        cls,
        currency: str,
        as_object: bool = False
    ) -> Union[Decimal, TimeStampedModel]:
        """
        Shows latest of 1 usd to `currency`
        Params:
            currency - one of available currency
        Raises:
            AssertionError - when wrong currency has been passed
            ValueError - when rate hasn`t been set
        Returns
            Decimal - current rate
        """
        check_currency(currency)

        if currency == BASE_CURRENCY:
            assert not as_object
            return Decimal("1")

        latest = cls.objects.filter(currency=currency).first()

        if latest is None:
            raise ValueError(f"Rate for {currency} hasn`t been set")

        return latest if as_object else latest.rate

    @classmethod
    def get(cls, from_currency: str, to_currency: str) -> Decimal:
        """
        Computes how much `to_currency` could be bought by 1 `from_currency`
        Raises:
            AssertionError - when one of passed currencies is wrong
            ValueError - when one of rates hasn`t been set
        Returns
            Decimal - current rate
        """
        from_rate = cls.of(from_currency)
        to_rate = cls.of(to_currency)

        return to_rate / from_rate


class Wallet(TimeStampedModel):
    """
    Wallet for user. User could have one wallet with one currency
    Stores amount of wallet
    """
    CURRENCIES = Choices(*CURRENCIES)

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    currency = StatusField(choices_name='CURRENCIES')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def amount_in(self, to_currency: str) -> Decimal:
        """
        Get's amount of wallet in different currencies.
        Params:
            to_params - currencies
        Raises:
            AssertionError - when wrong currency has been passed
            ValueError - when rates hasn`t been set
        Returns:
            Decimal - amount in selected currency
        """
        rate = ExchangeRate.get(self.currency, to_currency)
        return self.amount * rate

    @property
    def transactions(self) -> models.QuerySet:
        """
        Checks has transactions been prefetched to `_transactions` model
        if yes return them. Else get from db
        :return:
        """
        if not hasattr(self, '_transactions'):
            self._transactions = Transaction.objects.filter(
                Q(from_wallet__pk=self.pk) |
                Q(to_wallet__pk=self.pk)
            )
        return self._transactions


class Transaction(TimeStampedModel):
    """
    Stores info about transactions that has been proceed
    """
    CURRENCIES = Choices(*CURRENCIES)
    from_wallet = models.ForeignKey(
        Wallet,
        related_name='outgoing_transactions',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    to_wallet = models.ForeignKey(
        Wallet,
        related_name='incoming_transactions',
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    currency = StatusField(choices_name='CURRENCIES')

    class Meta:
        index_together = [
            ('from_wallet', 'to_wallet'),
        ]
