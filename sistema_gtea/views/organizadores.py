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
from django.contrib.auth.models import update_session_auth_hash # type: ignore
import string
import random
import json

'''
class OrganizadorAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        Organizador = Organizador.objects.filter(user__is_active = 1).order_by("id")
        Organizador = Organizadorerializer(Organizador, many=True).data
        #Aquí convertimos los valores de nuevo a un array
        if not Organizador:
            return Response({},400)
        for organizador in Organizador:
            organizador["materias_json"] = json.loads(organizador["materias_json"])

        return Response(Organizador, 200)

class OrganizadorView(generics.CreateAPIView):
    #Obtener usuario por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        organizador = get_object_or_404(Organizador, id = request.GET.get("id"))
        organizador = Organizadorerializer(organizador, many=False).data
        organizador["materias_json"] = json.loads(organizador["materias_json"])
        return Response(organizador, 200)
    

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password) #Cifrar la contraseña
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del estudiante
            organizador = Organizador.objects.create(user=user,
                                            clave_organizador= request.data["clave_organizador"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            cubiculo= request.data["cubiculo"],
                                            area_investigacion= request.data["area_investigacion"],
                                            materias_json= json.dumps(request.data["materias_json"]))
            organizador.save()

            return Response({"organizador_created_id": organizador.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrganizadorViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    #Contar el total de cada tipo de usuarios
    def get(self, request, *args, **kwargs):
        #Obtener total de admins
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista_admins = AdminSerializer(admin, many=True).data
        # Obtienes la cantidad de elementos en la lista
        total_admins = len(lista_admins)

        #Obtener total de Organizador
        Organizador = Organizador.objects.filter(user__is_active = 1).order_by("id")
        lista_Organizador = Organizadorerializer(Organizador, many=True).data
        #Aquí convertimos los valores de nuevo a un array
        if not lista_Organizador:
            return Response({},400)
        for organizador in lista_Organizador:
            organizador["materias_json"] = json.loads(organizador["materias_json"])
        
        total_Organizador = len(lista_Organizador)

        #Obtener total de Estudiantes
        Estudiantes = Estudiantes.objects.filter(user__is_active = 1).order_by("id")
        lista_Estudiantes = Estudianteserializer(Estudiantes, many=True).data
        total_Estudiantes = len(lista_Estudiantes)

        return Response({'admins': total_admins, 'Organizador': total_Organizador, 'Estudiantes:':total_Estudiantes }, 200)
    
    #Editar organizador
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        organizador = get_object_or_404(Organizador, id=request.data["id"])
        organizador.clave_organizador = request.data["clave_organizador"]
        organizador.fecha_nacimiento = request.data["fecha_nacimiento"]
        organizador.telefono = request.data["telefono"]
        organizador.curp = request.data["curp"].upper()
        organizador.rfc = request.data["rfc"].upper()
        organizador.edad = request.data["edad"]
        organizador.cubiculo = request.data["cubiculo"]
        organizador.area_investigacion = request.data["area_investigacion"]
        organizador.materias_json = json.dumps(request.data["materias_json"])
        organizador.save()
        temp = organizador.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = Organizadorerializer(organizador, many=False).data

        return Response(user,200)
    
    #Eliminar organizador
    def delete(self, request, *args, **kwargs):
        organizador = get_object_or_404(Organizador, id=request.GET.get("id"))
        try:
            organizador.user.delete()
            return Response({"details":"organizador eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

'''

class OrganizadorView(generics.GenericAPIView):
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request, *args, **kwargs):
            # Obtener el perfil del usuario autenticado
            admin = get_object_or_404(Administradores, user=request.user)
            serializer = AdminSerializer(admin)
            return Response(serializer.data, status=status.HTTP_200_OK)

        def put(self, request, *args, **kwargs):
            # Actualizar perfil
            admin = get_object_or_404(Administradores, user=request.user)
            serializer = AdminSerializer(admin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrganizadorViewEdit(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get("contrasena_actual")
        new_password = request.data.get("nueva_contrasena")
        confirm_password = request.data.get("confirmar_nueva_contrasena")

        if not authenticate(username=user.username, password=current_password):
            return Response({"error": "Contraseña actual incorrecta"}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Las contraseñas no coinciden"}, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        # Mantener sesión activa
        update_session_auth_hash(request, user)  

        return Response({"message": "Contraseña actualizada correctamente"}, status=status.HTTP_200_OK)