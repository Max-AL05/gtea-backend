from django.shortcuts import render, get_object_or_404 # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status, permissions # type: ignore
from sistema_gtea.models import Categoria
from sistema_gtea.serializers import CategoriaSerializer

# crear categoria
class CategoriaView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# LISTADO
class CategoriasAll(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# EDICIÓN Y BORRADO
class CategoriasViewEdit(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        categoria = get_object_or_404(Categoria, id=request.data["id"])
        
        # Asegúrate de que el frontend envíe estos nombres exactos
        categoria.nombre_categoria = request.data["nombre_categoria"]
        categoria.descripcion = request.data["descripcion"]
        
        categoria.save()
        
        categoria_data = CategoriaSerializer(categoria, many=False).data
        
        return Response(categoria_data, status=200)

    def delete(self, request, *args, **kwargs):
        categoria = get_object_or_404(Categoria, id=request.data["id"])
        categoria.delete()
        return Response({"message": "Categoría eliminada correctamente"}, status=status.HTTP_204_NO_CONTENT)