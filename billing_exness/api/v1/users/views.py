# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .serializers import CreateUserSerializer, UserSerializer


class CreateUserApiView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer) -> AbstractBaseUser:
        return serializer.save()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
