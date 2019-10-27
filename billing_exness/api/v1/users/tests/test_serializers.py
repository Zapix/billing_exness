# -*- coding: utf-8 -*-
import pytest

from billing_exness.users.tests.factories import UserFactory
from billing_exness.billing.constants import USD, EUR
from ..serializers import CreateUserSerializer

pytestmark = pytest.mark.django_db


class TestCreateUserSerializer:

    @pytest.mark.watch
    def test_required_fields(self):
        serializer = CreateUserSerializer(data={})

        assert not serializer.is_valid()
        for field in ['username', 'currency', 'password1']:
            assert field in serializer.errors

    @pytest.mark.watch
    def test_username_has_been_registerd_before(self):
        user = UserFactory.create()
        serializer = CreateUserSerializer(
            data={
                'username': user.get_username()
            }
        )
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    @pytest.mark.watch
    def test_password_do_not_match(self):
        serializer = CreateUserSerializer(
            data={
                'username': 'veryuniquename',
                'currency': EUR,
                'password1': 'v3ry$r0ngp4ssvvrd',
                'password2': 'wrongpass'
            }
        )

        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors, serializer.errors

    @pytest.mark.watch
    def test_save_success(self):
        serializer = CreateUserSerializer(
            data={
                'username': 'veryuniquename',
                'currency': EUR,
                'password1': 'v3ry$r0ngp4ssvvrd',
                'password2': 'v3ry$r0ngp4ssvvrd',
            }
        )

        assert serializer.is_valid()

        user = serializer.save()

        assert user.get_username() == 'veryuniquename'
        assert user.wallet.currency == EUR
