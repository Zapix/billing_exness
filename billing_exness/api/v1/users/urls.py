# -*- coding: utf-8 -*-
from django.urls import path

from .views import (
    CreateUserApiView,
    UserMeApiView,
    WalletApiView,
    PaymentApiView,
)

app_name = 'users'
urlpatterns = [
    path("", CreateUserApiView.as_view(), name='create'),
    path("me/", UserMeApiView.as_view(), name='me'),
    path("me/wallet/", WalletApiView.as_view(), name="wallet"),
    path("me/payment/", PaymentApiView.as_view(), name="payment")
]
