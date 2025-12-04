from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import *
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import Group, User
from sistema_gtea.models import *
from sistema_gtea.serializers import *
import json

# 1. LISTAR TODOS LOS ADMINISTRADORES
class AdminAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        admins = Administradores.objects.filter(user__is_active=1).order_by("id")
        lista_admins = AdminSerializer(admins, many=True).data
        return Response(lista_admins, 200)

# 2. VER UN ADMIN Y REGISTRAR NUEVO
class AdminView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # Obtener un admin por ID
    def get(self, request, *args, **kwargs):
        admin_id = request.GET.get("id")
        admin = get_object_or_404(Administradores, id=admin_id)
        serializer = AdminSerializer(admin, many=False).data
        return Response(serializer, 200)
    
    # Registrar nuevo admin
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
            role = request.data.get('rol', 'Administrador')

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

            admin = Administradores.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password = user.password,
                telefono = request.data.get("telefono",),
                biografia = request.data.get("biografia",)
            )
            admin.save()

            return Response({
                "admin_created_id": admin.id,
                "message": "Administrador creado exitosamente"
            }, status=201)

        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminsViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
#dashboard
    def get(self, request, *args, **kwargs):
        total_admins = Administradores.objects.filter(user__is_active=1).count()
        total_organizadores = Organizador.objects.filter(user__is_active=1).count()
        total_estudiantes = Estudiantes.objects.filter(user__is_active=1).count()

        total_usuarios = total_admins + total_organizadores + total_estudiantes

        return Response({
            'Administradores': total_admins, 
            'Organizadores': total_organizadores, 
            'Estudiantes': total_estudiantes,
            'Total usuarios': total_usuarios
        }, 200)
    
    # Editar Administrador
    def put(self, request, *args, **kwargs):
        admin_id = request.data.get("id")
        admin = get_object_or_404(Administradores, id=admin_id)
        
        admin.telefono = request.data["telefono"]
        admin.biografia = request.data["biografia"]
        admin.first_name = request.data["first_name"]
        admin.last_name = request.data["last_name"]
            
        admin.save()

        user_obj = admin.user
        user_obj.first_name = request.data["first_name"]
        user_obj.last_name = request.data["last_name"]
        user_obj.save()

        serializer = AdminSerializer(admin, many=False).data
        return Response(serializer, 200)
    
    # Eliminar Administrador
    def delete(self, request, *args, **kwargs):
        admin_id = request.GET.get("id")
        admin = get_object_or_404(Administradores, id=admin_id)
        try:
            admin.user.delete()
            return Response({"details": "Administrador eliminado correctamente"}, 200)
        except Exception as e:
            return Response({"details": "Error al eliminar"}, 400)