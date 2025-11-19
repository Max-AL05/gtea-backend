from django.shortcuts import render # type: ignore
from django.db.models import * # type: ignore
from django.db import transaction # type: ignore
from sistema_gtea.serializers import *
from sistema_gtea.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication # type: ignore
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView # type: ignore
from rest_framework import permissions # type: ignore
from rest_framework import generics # type: ignore
from rest_framework import status # type: ignore
from rest_framework.authtoken.views import ObtainAuthToken # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.decorators import api_view # type: ignore
from rest_framework.reverse import reverse # type: ignore
from rest_framework import viewsets # type: ignore
from django.shortcuts import get_object_or_404 # type: ignore
from django.core import serializers # type: ignore
from django.utils.html import strip_tags # type: ignore
from django.contrib.auth import authenticate, login # type: ignore
from django.contrib.auth.models import Group # type: ignore
from django.contrib.auth import get_user_model # type: ignore
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from django_filters import rest_framework as filters # type: ignore
from datetime import datetime
from django.conf import settings # type: ignore
from django.template.loader import render_to_string # type: ignore
import string
import random

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_active:
            roles = user.groups.all()
            role_names = []
            for role in roles:
                role_names.append(role.name)
            #Si solo es un rol especifico asignamos el elemento 0
            role_names = role_names[0]

            #Esta función genera la clave dinámica (token) para iniciar sesión
            token, created = Token.objects.get_or_create(user=user)

            if role_names == 'estudiante':
                estudiante = Estudiantes.objects.filter(user=user).first()
                estudiante = Estudianteserializer(estudiante).data
                estudiante["token"] = token.key
                estudiante["rol"] = "estudiante"
                return Response(estudiante,200)
            if role_names == 'organizador':
                organizador = Organizador.objects.filter(user=user).first()
                organizador = OrganizadorSerializer(organizador).data
                organizador["token"] = token.key
                organizador["rol"] = "organizador"
                return Response(organizador,200)
            if role_names == 'administrador':
                user = AdminSerializer(user, many=False).data #userSerializer
                user['token'] = token.key
                user["rol"] = "administrador"
                return Response(user,200)
            else:
                return Response({"details":"Forbidden"},403)
                pass

        return Response({}, status=status.HTTP_403_FORBIDDEN)



class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        print("logout")
        user = request.user
        print(str(user))
        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()

            return Response({'logout':True})


        return Response({'logout': False})
