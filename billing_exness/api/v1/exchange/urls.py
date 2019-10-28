# -*- coding: utf-8 -*-
from django.urls import path

from .views import ExchangeRateApiView

app_name = 'exchange'
urlpatterns = [
    path("<str:currency>/", ExchangeRateApiView.as_view(), name="rate")
]
