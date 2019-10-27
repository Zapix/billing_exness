# -*- coding: utf-8 -*-
from django.urls import path, include

from rest_framework.authtoken import views

from .views import ObtainAuthTokenWithInfo

urlpatterns = [
    path('auth/', ObtainAuthTokenWithInfo.as_view()),
]
