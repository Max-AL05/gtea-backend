from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from sistema_gtea.serializers import *
from sistema_gtea.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions # Importante
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random

class CustomAuthToken(ObtainAuthToken):
    # 1. ESTA LÍNEA ES OBLIGATORIA PARA EL LOGIN (Deja entrar sin token)
    permission_classes = (permissions.AllowAny,) 

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if user.is_active:
            roles = user.groups.all()
            if roles.exists():
                # Obtenemos el nombre del rol (Ej: "Estudiante")
                role_name = roles[0].name 
            else:
                role_name = None

            # Generar token
            token, created = Token.objects.get_or_create(user=user)

            # 2. COMPARACIÓN CORREGIDA (Acepta mayúsculas y minúsculas)
            if role_name in ['Estudiante', 'estudiante']:
                estudiante = Estudiantes.objects.filter(user=user).first()
                # Validación extra por si el perfil no existe
                if estudiante:
                    estudiante_data = Estudianteserializer(estudiante).data
                    estudiante_data["token"] = token.key
                    estudiante_data["rol"] = "Estudiante"
                    return Response(estudiante_data, 200)
                else:
                    return Response({"details": "Perfil de estudiante no encontrado"}, 400)

            elif role_name in ['Organizador', 'organizador']:
                organizador = Organizador.objects.filter(user=user).first()
                if organizador:
                    organizador_data = OrganizadorSerializer(organizador).data
                    organizador_data["token"] = token.key
                    organizador_data["rol"] = "Organizador"
                    return Response(organizador_data, 200)
                else:
                    return Response({"details": "Perfil de organizador no encontrado"}, 400)

            elif role_name in ['Administrador', 'administrador', 'Admin', 'admin']:
                user_data = AdminSerializer(user, many=False).data
                user_data['token'] = token.key
                user_data["rol"] = "Administrador"
                return Response(user_data, 200)
            
            else:
                # Si llega aquí es porque el rol no coincidió con ninguno
                return Response({"details": f"Forbidden - Rol detectado: {role_name}"}, 403)

        return Response({}, status=status.HTTP_403_FORBIDDEN)


class Logout(generics.GenericAPIView):
    # Para cerrar sesión, lo ideal es requerir que estén autenticados
    permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request, *args, **kwargs):
        print("logout")
        user = request.user
        print(str(user))
        if user.is_active:
            # Borrar el token cierra la sesión en el dispositivo
            request.user.auth_token.delete()
            return Response({'logout': True}, 200)

        return Response({'logout': False}, 400)