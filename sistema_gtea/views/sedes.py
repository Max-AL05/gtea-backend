from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
#from rest_framework.parsers import MultiPartParser, FormParser 
from sistema_gtea.models import Sede
from sistema_gtea.serializers import SedeSerializer
import json

def es_admin(user):
    return user.is_authenticated and user.groups.filter(name__in=['Administrador', 'Admin', 'administrador']).exists()

class SedesAll(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        sedes = Sede.objects.all().order_by("id")
        sedes_data = SedeSerializer(sedes, many=True).data
        
        if not sedes_data:
            return Response([], 200)
            
        for sede in sedes_data:
            try:
                sede["recursos_json"] = json.loads(sede["recursos_json"])
            except (TypeError, json.JSONDecodeError):
                sede["recursos_json"] = []
                
        return Response(sedes_data, 200)

class SedeView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    #parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        sede = get_object_or_404(Sede, id=request.GET.get("id"))
        sede_data = SedeSerializer(sede, many=False).data
        
        try:
            sede_data["recursos_json"] = json.loads(sede_data["recursos_json"])
        except (TypeError, json.JSONDecodeError):
            sede_data["recursos_json"] = []
            
        return Response(sede_data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores pueden crear sedes."}, status=403)

        data = request.data.copy()
        
        if "recursos_json" in data:
            if not isinstance(data["recursos_json"], str):
                data["recursos_json"] = json.dumps(data["recursos_json"])

        serializer = SedeSerializer(data=data)
        if serializer.is_valid():
            sede_guardada = serializer.save()
            return Response({"sede_created_id": sede_guardada.id}, 201)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SedesViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    #parser_classes = (MultiPartParser, FormParser)
    
    # Editar Sede
    def put(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores pueden editar."}, status=403)

        sede = get_object_or_404(Sede, id=request.data["id"])
        
        sede.edificio = request.data["edificio"]
        sede.aula = request.data["aula"]
        sede.capacidad = request.data["capacidad"]
        
        if "recursos_json" in request.data:
             recursos = request.data["recursos_json"]
             if not isinstance(recursos, str):
                 sede.recursos_json = json.dumps(recursos)
             else:
                 sede.recursos_json = recursos

        sede.save()
        
        sede_data = SedeSerializer(sede, many=False).data
        return Response(sede_data, 200)
    
    #Eliminar Sede
    def delete(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores pueden eliminar."}, status=403)

        sede = get_object_or_404(Sede, id=request.GET.get("id"))
        try:
            sede.delete()
            return Response({"details": "Sede eliminada"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)