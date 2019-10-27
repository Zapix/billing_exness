# -*- coding: utf-8 -*-
from django.urls import path

from .views import CreateUserApiView

app_name = 'users'
urlpatterns = [
    path("", CreateUserApiView.as_view(), name='create'),
]
