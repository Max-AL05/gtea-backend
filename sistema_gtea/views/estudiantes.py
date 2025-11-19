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
import string
import random
import json

class EstudiantesALL(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        Estudiantes = Estudiantes.objects.filter(user__is_active = 1).order_by("id")
        Estudiantes = Estudianteserializer(Estudiantes, many=True).data
        
        return Response(Estudiantes, 200)

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
            estudiante = Estudiantes.objects.create(user=user,
                                            clave_estudiante= request.data["clave_estudiante"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            estudiante.save()

            return Response({"estudiante_created_id": estudiante.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EstudiantesViewEdit(generics.CreateAPIView):
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
        lista_Organizador = OrganizadorSerializer(Organizador, many=True).data
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
    
    #Editar estudiante
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        estudiante = get_object_or_404(Estudiantes, id=request.data["id"])
        estudiante.clave_estudiante = request.data["clave_estudiante"]
        estudiante.fecha_nacimiento = request.data["fecha_nacimiento"]
        estudiante.telefono = request.data["telefono"]
        estudiante.curp = request.data["curp"].upper()
        estudiante.rfc = request.data["rfc"].upper()
        estudiante.edad = request.data["edad"]
        estudiante.ocupacion = request.data["ocupacion"]
        estudiante.save()
        temp = estudiante.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = Estudianteserializer(estudiante, many=False).data

        return Response(user,200)
    
    #Eliminar estudiante
    def delete(self, request, *args, **kwargs):
        estudiante = get_object_or_404(Estudiantes, id=request.GET.get("id"))
        try:
            estudiante.user.delete()
            return Response({"details":"estudiante eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)