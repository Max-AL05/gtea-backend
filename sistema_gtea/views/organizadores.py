from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import *
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import Group, User
from sistema_gtea.models import *
from sistema_gtea.serializers import *
import json

# 1. LISTAR TODOS LOS ORGANIZADORES
class OrganizadorAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        organizadores = Organizador.objects.filter(user__is_active=1).order_by("id")
        lista_organizadores = OrganizadorSerializer(organizadores, many=True).data
        return Response(lista_organizadores, 200)

# 2. VER UN ORGANIZADOR Y REGISTRAR NUEVO
class OrganizadorView(generics.CreateAPIView):
    # permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request, *args, **kwargs):
        organizador_id = request.GET.get("id")
        organizador = get_object_or_404(Organizador, id=organizador_id)
        serializer = OrganizadorSerializer(organizador, many=False).data
        return Response(serializer, 200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        email = request.data.get('email')
        if not email:
            return Response({"message": "El campo 'email' es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        
        if password != confirm_password:
             return Response({"message": "Las contraseñas no coinciden"}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return Response({"message": f"El correo {email} ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            role = request.data.get('rol', 'Organizador')

            user = User.objects.create(
                username = email,
                email = email,
                first_name = first_name,
                last_name = last_name,
                is_active = 1
            )
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            organizador = Organizador.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                telefono = request.data.get("telefono", ""),
                biografia = request.data.get("biografia", "")
            )
            organizador.save()

            return Response({
                "organizador_created_id": organizador.id,
                "message": "Organizador creado exitosamente"
            }, status=201)

        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 3. DASHBOARD, EDICIÓN Y ELIMINACIÓN
class OrganizadorViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        total_admins = Administradores.objects.filter(user__is_active=1).count()
        total_organizadores = Organizador.objects.filter(user__is_active=1).count()
        total_estudiantes = Estudiantes.objects.filter(user__is_active=1).count()

        return Response({
            'admins': total_admins, 
            'Organizador': total_organizadores, 
            'Estudiantes': total_estudiantes 
        }, 200)
    
    # Editar Organizador
    def put(self, request, *args, **kwargs):
        organizador_id = request.data.get("id")
        organizador = get_object_or_404(Organizador, id=organizador_id)
        
        organizador.telefono = request.data.get("telefono", organizador.telefono)
        organizador.biografia = request.data.get("biografia", organizador.biografia)
        
        #if 'imagen' in request.FILES:
            #organizador.imagen = request.FILES['imagen']
        
        organizador.first_name = request.data.get("first_name", organizador.first_name)
        organizador.last_name = request.data.get("last_name", organizador.last_name)
        organizador.save()

        user_obj = organizador.user
        user_obj.first_name = request.data.get("first_name", user_obj.first_name)
        user_obj.last_name = request.data.get("last_name", user_obj.last_name)
        user_obj.save()

        serializer = OrganizadorSerializer(organizador, many=False).data
        return Response(serializer, 200)
    
    # Eliminar Organizador
    def delete(self, request, *args, **kwargs):
        organizador_id = request.GET.get("id")
        organizador = get_object_or_404(Organizador, id=organizador_id)
        try:
            organizador.user.delete()
            return Response({"details": "Organizador eliminado correctamente"}, 200)
        except Exception as e:
            return Response({"details": "Error al eliminar"}, 400)