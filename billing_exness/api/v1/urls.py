# -*- coding: utf-8 -*-
from django.urls import path, include

from .views import ObtainAuthTokenWithInfo

app_name = 'api_v1'
urlpatterns = [
    path('auth/', ObtainAuthTokenWithInfo.as_view(), name='auth'),
    path('users/', include('billing_exness.api.v1.users.urls')),
]
