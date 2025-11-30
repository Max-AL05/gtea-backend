from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.db.models import *
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import Group, User
from sistema_gtea.models import *
from sistema_gtea.views import estudiantes # Importación circular fix (si se requiere)
from sistema_gtea.serializers import *
import json

# 1. LISTAR TODOS LOS ESTUDIANTES
class EstudiantesALL(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, *args, **kwargs):
        estudiantes = Estudiantes.objects.filter(user__is_active=1).order_by("id")
        lista_estudiantes = Estudianteserializer(estudiantes, many=True).data
        return Response(lista_estudiantes, 200)

# 2. VER UN ESTUDIANTE Y REGISTRAR NUEVO
class EstudiantesView(generics.CreateAPIView):
    # permission_classes = (permissions.IsAuthenticated,) 

    def get(self, request, *args, **kwargs):
        estudiante_id = request.GET.get("id")
        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)
        serializer = Estudianteserializer(estudiante, many=False).data
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

        email = request.data.get('email')
        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            return Response({"message": f"El correo {email} ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            role = request.data.get('rol', 'Estudiante')

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

            estudiante = Estudiantes.objects.create(
                user=user,
                telefono = request.data.get("telefono", "")
            )
            estudiante.save()

            return Response({
                "estudiante_created_id": estudiante.id,
                "message": "Usuario creado exitosamente"
            }, status=201)

        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 3. ESTADÍSTICAS, EDICIÓN Y ELIMINACIÓN
class EstudiantesViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
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
    
    def put(self, request, *args, **kwargs):
        estudiante_id = request.data.get("id")
        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)
        
        estudiante.telefono = request.data.get("telefono", estudiante.telefono)
        estudiante.biografia = request.data.get("biografia", estudiante.biografia)
        
        if 'imagen' in request.FILES:
            estudiante.imagen = request.FILES['imagen']
            
        estudiante.save()

        user_obj = estudiante.user
        user_obj.first_name = request.data.get("first_name", user_obj.first_name)
        user_obj.last_name = request.data.get("last_name", user_obj.last_name)
        user_obj.save()

        serializer = Estudianteserializer(estudiante, many=False).data
        return Response(serializer, 200)
    
    def delete(self, request, *args, **kwargs):
        estudiante_id = request.GET.get("id")
        estudiante = get_object_or_404(Estudiantes, id=estudiante_id)
        try:
            estudiante.user.delete()
            return Response({"details": "Estudiante eliminado correctamente"}, 200)
        except Exception as e:
            return Response({"details": "Error al eliminar el estudiante"}, 400)