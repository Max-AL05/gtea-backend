from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser 
from sistema_gtea.models import Categoria
from sistema_gtea.serializers import CategoriaSerializer
import json

def es_admin(user):
    return user.is_authenticated and user.groups.filter(name__in=['Administrador', 'Admin', 'administrador']).exists()

class CategoriaAll(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        categorias = Categoria.objects.all().order_by("id")
        categorias_data = CategoriaSerializer(categorias, many=True).data
        
        if not categorias_data:
            return Response([], 200)
            
        return Response(categorias_data, 200)

class CategoriaView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        categoria = get_object_or_404(Categoria, id=request.GET.get("id"))
        categoria_data = CategoriaSerializer(categoria, many=False).data
        return Response(categoria_data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores pueden crear categorías."}, status=403)

        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            categoria_guardada = serializer.save()
            return Response({"categoria_created_id": categoria_guardada.id}, 201)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoriaViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    #editar categoría
    def put(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores pueden editar."}, status=403)

        categoria = get_object_or_404(Categoria, id=request.data["id"])
        
        categoria.nombre_categoria = request.data["nombre_categoria"]
        categoria.descripcion = request.data["descripcion"]
        
        categoria.save()
        
        categoria_data = CategoriaSerializer(categoria, many=False).data
        return Response(categoria_data, 200)
    
    #eliminar categoria
    def delete(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores pueden eliminar."}, status=403)

        categoria = get_object_or_404(Categoria, id=request.GET.get("id"))
        try:
            categoria.delete()
            return Response({"details": "Categoría eliminada"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)