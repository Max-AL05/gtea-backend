from django.shortcuts import render# type: ignore
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
#from django.contrib.auth.models import update_session_auth_hash # type: ignore
from rest_framework import generics # type: ignore
from rest_framework import permissions # type: ignore
from rest_framework import status # type: ignore
from django.contrib.auth.models import User # type: ignore
from sistema_gtea.serializers import UserSerializer # type: ignore
import string
import random
import json

class AdminAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        
        return Response(lista, 200)

#iniciar sesion
class AdminView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]  

    def post(self, request, *args, **kwargs):
        email = request.data.get("correo_electronico")
        password = request.data.get("contrasena")

        user = authenticate(username=email, password=password)

        if not user:
            return Response({"error": "Correo o contraseña incorrectos"}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user) # Obtener o crear token

        user_data = UserSerializer(user).data

        return Response({
            "token": token.key,
            "user": user_data,
            "message": "Inicio de sesión exitoso"
        }, status=status.HTTP_200_OK)

#crear cuenta
class AdminView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        if not request.data.get("acepta_terminos"):
            return Response({"error": "Debes aceptar los términos y condiciones"}, status=status.HTTP_400_BAD_REQUEST)

        first_name = request.data.get("nombre")
        last_name = request.data.get("apellidos")
        email = request.data.get("correo_institucional")
        password = request.data.get("contraseña")
        confirm_password = request.data.get("confirmar_contraseña")
        rol = request.data.get("rol", "Administrador")  # Por defecto Admin

        #validaciones
        if password != confirm_password:
            return Response({"error": "Las contraseñas no coinciden"}, status=status.HTTP_400_BAD_REQUEST)

        if not email.endswith("@institucion.edu"):
            return Response({"error": "El correo debe ser institucional (@institucion.edu)"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Este correo ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear usuario en auth user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=True
        )

        # Asignar rol
        group, created = Group.objects.get_or_create(name=rol)
        group.user_set.add(user)

        # Crear perfil según rol
        if rol == "Admin":
            admin = Administradores.objects.create(
                user=user,
                clave_admin="",
                telefono="",
                rfc="",
                edad=0,
                ocupacion=""
            )
            admin.save()
        elif rol == "Organizador":
            organizador = Organizador.objects.create(
                user=user,
                clave_organizador="",
                telefono="",
                rfc="",
                edad=0,
                ocupacion=""
            )
            organizador.save()
        elif rol == "Estudiante":
            estudiante = Estudiantes.objects.create(
                user=user,
                clave_estudiante="",
                telefono="",
                rfc="",
                edad=0,
                ocupacion=""
            )
            estudiante.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data,
            "message": "Cuenta creada exitosamente"
        }, status=status.HTTP_201_CREATED)

# informacion perfil
class AdminsViewEdit(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Obtener perfil (Get simple o por ID)
    def get(self, request, *args, **kwargs):
        # Si mandan ID, buscamos ese, si no, intentamos buscar el del usuario logueado
        id_admin = request.query_params.get('id')
        if id_admin:
            admin = get_object_or_404(Administradores, id=id_admin)
        else:
            # Busca el perfil del usuario que hace la petición
            admin = get_object_or_404(Administradores, user=request.user)
            
        serializer = AdminSerializer(admin)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # 1. Buscar el perfil de Administrador por ID
        admin_profile = get_object_or_404(Administradores, id=request.data["id"])
        
        # 2. Actualizar datos del modelo Administradores (Perfil extendido)
        admin_profile.telefono = request.data.get("telefono", admin_profile.telefono)
        admin_profile.biografia = request.data.get("biografia", admin_profile.biografia)
        
        # Actualizamos también los campos espejo si se desea mantener sincronía
        admin_profile.first_name = request.data.get("first_name", admin_profile.first_name)
        admin_profile.last_name = request.data.get("last_name", admin_profile.last_name)
        
        admin_profile.save()

        # 3. Actualizar datos del modelo User de Django (Login básico)
        user_django = admin_profile.user
        if user_django:
            user_django.first_name = request.data.get("first_name", user_django.first_name)
            user_django.last_name = request.data.get("last_name", user_django.last_name)
            user_django.email = request.data.get("email", user_django.email)

        password_actual = request.data.get("password_actual") # Contraseña Actual
        password_nueva = request.data.get("password_nueva") # Nueva
        password_confirmacion = request.data.get("password_nueva_confirm") # Confirmación

        # Solo entramos aquí si el usuario escribió algo en los campos de contraseña
        if password_actual and password_nueva and password_confirmacion:
                
            # A. Verificar si la contraseña actual es correcta
            if user_django.check_password(password_actual):
                    
                # B. Verificar que la nueva y la confirmación sean iguales
                if password_nueva == password_confirmacion:
                        
                    # C. Establecer la nueva contraseña (encriptada para el login)
                    user_django.set_password(password_nueva)
                        
                    # D. Actualizar el campo espejo en el modelo Administradores (Texto plano si así lo tienes)
                    admin_profile.password = password_nueva
                    admin_profile.save()
                else:
                    return Response({"error": "Las nuevas contraseñas no coinciden"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "La contraseña actual es incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardamos el usuario de Django
            user_django.save()

        # 4. Responder con los datos actualizados
        serializer = AdminSerializer(admin_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''''
class AdminView(generics.CreateAPIView): #obtener tablas
    #Obtener usuario por ID
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data

        return Response(admin, 200)
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

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

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
'''''     
'''''
class AdminsViewEdit(generics.CreateAPIView):
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
    
    #Editar administrador
    def put(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.data["id"])
        admin.email = request.data["email"]
        admin.telefono = request.data["telefono"]
        admin.biografia = request.data["biografia"]
        admin.save()
        temp = admin.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = AdminSerializer(admin, many=False).data

        return Response(user,200)
    
    #Eliminar administrador

    def delete(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        try:
            admin.user.delete()
            return Response({"details":"Administrador eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
'''''
'''''
class AdminView(generics.GenericAPIView):
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
'''''
'''''
class AdminViewEdit(generics.GenericAPIView):

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
'''''