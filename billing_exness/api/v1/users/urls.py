# -*- coding: utf-8 -*-
from django.urls import path

from .views import CreateUserApiView, UserMeApiView

app_name = 'users'
urlpatterns = [
    path("", CreateUserApiView.as_view(), name='create'),
    path("me/", UserMeApiView.as_view(), name='me'),
]
