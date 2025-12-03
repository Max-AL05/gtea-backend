from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser 
from sistema_gtea.models import Evento
from sistema_gtea.serializers import EventoSerializer
import json

# Función auxiliar para validar si es Admin
def es_admin(user):
    return user.groups.filter(name__in=['Administrador', 'Admin', 'administrador']).exists()

class EventosAll(generics.CreateAPIView):
    # Todos los usuarios logueados pueden ver la lista
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, *args, **kwargs):
        eventos = Evento.objects.all().order_by("id")
        eventos_data = EventoSerializer(eventos, many=True).data
        
        if not eventos_data:
            return Response([], 200)
            
        for evento in eventos_data:
            try:
                evento["publico_json"] = json.loads(evento["publico_json"])
            except (TypeError, json.JSONDecodeError):
                evento["publico_json"] = []
                
        return Response(eventos_data, 200)

class EventoView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    #Ver detalle (Público para usuarios logueados)
    def get(self, request, *args, **kwargs):
        evento = get_object_or_404(Evento, id=request.GET.get("id"))
        evento_data = EventoSerializer(evento, many=False).data
        
        try:
            evento_data["publico_json"] = json.loads(evento_data["publico_json"])
        except (TypeError, json.JSONDecodeError):
            evento_data["publico_json"] = []
            
        return Response(evento_data, 200)

    #Crear Evento (SOLO ADMIN)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores."}, status=403)

        data = request.data.copy()
        
        if "publico_json" in data:
            if not isinstance(data["publico_json"], str):
                data["publico_json"] = json.dumps(data["publico_json"])

        evento = EventoSerializer(data=data)
        if evento.is_valid():
            evento_guardado = evento.save()
            return Response({"evento_created_id": evento_guardado.id}, 201)
            
        return Response(evento.errors, status=status.HTTP_400_BAD_REQUEST)

# Editar evento
class EventosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    
    #Editar Evento (SOLO ADMIN)
    def put(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores."}, status=403)

        evento = get_object_or_404(Evento, id=request.data["id"])
        
        evento.nombre_evento = request.data["nombre_evento"]
        evento.descripcion = request.data["descripcion"]
        evento.categoria = request.data["categoria"] 
        evento.organizador = request.data["organizador"]
        evento.lugar = request.data["lugar"]
        evento.modalidad = request.data["modalidad"]
        evento.fecha_inicio = request.data["fecha_inicio"]
        evento.fecha_fin = request.data["fecha_fin"]
        evento.cupo = request.data["cupo"]
        
        if "publico_json" in request.data:
             publico = request.data["publico_json"]
             if not isinstance(publico, str):
                 evento.publico_json = json.dumps(publico)
             else:
                 evento.publico_json = publico

        if 'imagen' in request.FILES:
            evento.imagen = request.FILES['imagen']

        evento.save()
        
        evento_data = EventoSerializer(evento, many=False).data
        return Response(evento_data, 200)
    
    # Eliminar Evento (SOLO ADMIN)
    def delete(self, request, *args, **kwargs):
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores."}, status=403)

        evento = get_object_or_404(Evento, id=request.GET.get("id"))
        try:
            evento.delete()
            return Response({"details": "Evento eliminado"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)
        

    def get(self, request, *args, **kwargs):
        from sistema_gtea.models import Evento, Categoria

        total_eventos = Evento.objects.count()

        total_categorias = Categoria.objects.count()
        
        categoria_top = Evento.objects.values('categoria') \
                             .annotate(total=Count('id')) \
                             .order_by('-total') \
                             .first()

        return Response({
            'Total eventos': total_eventos,
            'Total categorias': total_categorias,
            'Categoria mas usada': {
                'Nombre': categoria_top,
            }
        }, 200)