from django.shortcuts import render # type: ignore
from django.db.models import * # type: ignore
from django.db import transaction # type: ignore
from sistema_gtea.serializers import * # type: ignore
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
from rest_framework.parsers import MultiPartParser, FormParser # type: ignore
import string
import random
import json

class EstudiantesALL(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        Estudiantes = Estudiantes.objects.filter(user__is_active = 1).order_by("id")
        Estudiantes = Estudianteserializer(Estudiantes, many=True).data
        
        return Response(Estudiantes, 200)

#login
class estudianteView(generics.CreateAPIView):
    #Obtener usuario por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        estudiante = get_object_or_404(Estudiantes, id = request.GET.get("id"))
        estudiante = Estudianteserializer(estudiante, many=False).data
        return Response(estudiante, 200)
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # 1. Validar que las contraseñas coincidan (Nuevo requerimiento del diseño)
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if password != confirm_password:
             return Response({"message": "Las contraseñas no coinciden"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validar usuario existente
        email = request.data.get('email')
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            return Response({"message": f"El correo {email} ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Crear el Usuario Base (User Model)
        # Usamos .get() para evitar errores si el campo no viene, aunque el front debería validarlo
        first_name = request.data.get('first_name') # "Nombre" en el diseño
        last_name = request.data.get('last_name')   # "Apellidos" en el diseño
        
        # Asumimos que si se registran desde esta pantalla, son Estudiantes por defecto
        role = request.data.get('rol', 'Estudiante') 

        try:
            user = User.objects.create(
                username = email, # Usamos el email como username para el login
                email = email,
                first_name = first_name,
                last_name = last_name,
                is_active = 1
            )
            user.set_password(password)
            user.save()

            # Asignar grupo
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            # 4. Crear el Perfil de Estudiante (Datos opcionales)
            # Como el diseño NO pide CURP ni RFC al inicio, usamos cadenas vacías "" o None.
            # El usuario llenará esto después en la pantalla de "Editar Perfil".
            estudiante = Estudiantes.objects.create(
                user=user,
                clave_estudiante= request.data.get("clave_estudiante", ""), # Opcional
                fecha_nacimiento= request.data.get("fecha_nacimiento", None), # Opcional
                curp= request.data.get("curp", "").upper(), # Opcional
                rfc= request.data.get("rfc", "").upper(), # Opcional
                edad= request.data.get("edad", None), # Opcional
                telefono= request.data.get("telefono", ""), # Opcional
                ocupacion= request.data.get("ocupacion", "") # Opcional
            )
            estudiante.save()

            return Response({
                "estudiante_created_id": estudiante.id,
                "message": "Usuario creado exitosamente"
            }, status=201)

        except Exception as e:
            # Si algo falla, el @transaction.atomic deshace todo
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class EstudiantesViewEdit(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    # Agregamos parsers para poder recibir imágenes y texto al mismo tiempo
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        # 1. Obtener el usuario autenticado y su perfil de estudiante
        user = request.user
        estudiante = get_object_or_404(Estudiantes, user=user)

        # 2. Actualizar datos del Modelo User (Nombre y Apellidos)
        # Usamos .get(campo, valor_actual) para mantener el dato viejo si no envían nada nuevo
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.save()

        # 3. Actualizar datos del Modelo Estudiantes
        estudiante.telefono = request.data.get("telefono", estudiante.telefono)
        estudiante.biografia = request.data.get("biografia", estudiante.biografia)

        # 4. Manejo de la Foto de Perfil
        # El frontend debe enviar el archivo con la key 'imagen'
        if 'imagen' in request.FILES:
            estudiante.imagen = request.FILES['imagen']

        estudiante.save()

        return Response({"message": "Perfil actualizado correctamente"}, status=200)    

from sistema_gtea.views.estudiantes import (
    estudianteView,       # <--- La vista de registro
    EstudiantesALL,       # <--- La vista de lista
    EstudiantesViewEdit  # <--- La vista de edición  # <--- La vista de password     # <--- La vista de login
)