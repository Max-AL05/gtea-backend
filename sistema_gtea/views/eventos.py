from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser 
from sistema_gtea.models import Evento, Categoria, Organizador
from sistema_gtea.serializers import EventoSerializer
import json

# Funciones auxiliares de permisos
def es_admin(user):
    return user.groups.filter(name__in=['Administrador', 'Admin', 'administrador']).exists()

def es_organizador(user):
    return user.is_authenticated and user.groups.filter(name__in=['Organizador', 'organizador']).exists()

# -------------------------------------------------------------------------
# VISTA PARA LISTAR EVENTOS (PÚBLICO Y FILTRADO)
# -------------------------------------------------------------------------
class EventosAll(generics.ListAPIView):
    # Permitimos que cualquiera (incluso no logueados) vea la lista
    permission_classes = (permissions.AllowAny,)
    serializer_class = EventoSerializer

    def get(self, request, *args, **kwargs):
        # 1. Por defecto, traemos TODOS los eventos (Objetivo: cualquier persona puede ver todo)
        eventos = Evento.objects.select_related('organizador').all().order_by("id")

        # 2. Lógica de filtro opcional:
        # Si el usuario es organizador Y envía el parámetro 'mis_eventos=true' en la URL
        ver_mis_eventos = request.query_params.get('mis_eventos') == 'true'

        if es_organizador(request.user) and ver_mis_eventos:
            try:
                perfil_org = Organizador.objects.get(user=request.user)
                eventos = eventos.filter(organizador=perfil_org)
            except Organizador.DoesNotExist:
                return Response({"details": "No se encontró tu perfil de organizador."}, status=400)

        # 3. Serialización
        eventos_data = EventoSerializer(eventos, many=True).data

        if not eventos_data:
            return Response([], 200)

        # Procesar el campo JSON manual (según tu modelo)
        for evento in eventos_data:
            try:
                if evento["publico_json"]:
                    evento["publico_json"] = json.loads(evento["publico_json"])
                else:
                    evento["publico_json"] = []
            except (TypeError, json.JSONDecodeError):
                evento["publico_json"] = []

        return Response(eventos_data, 200)

# -------------------------------------------------------------------------
# VISTA PARA CREAR Y VER UN EVENTO INDIVIDUAL
# -------------------------------------------------------------------------
class EventoView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        # Obtener un evento específico por ID
        evento_id = request.GET.get("id")
        if not evento_id:
            return Response({"details": "Falta el parámetro id"}, status=400)
            
        evento = get_object_or_404(Evento, id=evento_id)
        evento_data = EventoSerializer(evento, many=False).data
        
        try:
            if evento_data["publico_json"]:
                evento_data["publico_json"] = json.loads(evento_data["publico_json"])
            else:
                evento_data["publico_json"] = []
        except (TypeError, json.JSONDecodeError):
            evento_data["publico_json"] = []
            
        return Response(evento_data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Solo admins u organizadores pueden crear
        if not (es_admin(request.user) or es_organizador(request.user)):
            return Response({"details": "Acción denegada. No tienes permisos para crear eventos."}, status=403)

        data = request.data.copy()
        
        # Manejo del JSON manual
        if "publico_json" in data:
            if not isinstance(data["publico_json"], str):
                data["publico_json"] = json.dumps(data["publico_json"])

        # Asignación automática del Organizador
        if es_organizador(request.user):
            try:
                perfil = Organizador.objects.get(user=request.user)
                # Forzamos que el evento pertenezca al usuario logueado
                data["organizador"] = perfil.id
            except Organizador.DoesNotExist:
                return Response({"details": "No tienes un perfil de organizador asociado."}, status=400)

        evento = EventoSerializer(data=data)
        if evento.is_valid():
            evento_guardado = evento.save()
            return Response({"evento_created_id": evento_guardado.id}, 201)
            
        return Response(evento.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------------------------------------------------
# VISTA PARA EDITAR Y BORRAR (SOLO ADMINS SEGÚN TU LÓGICA ACTUAL)
# -------------------------------------------------------------------------
class EventosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    
    def put(self, request, *args, **kwargs):
        # Nota: Aquí tal vez quieras permitir que el organizador edite SU propio evento.
        # Por ahora lo dejé solo para Admin como estaba en tu archivo original.
        if not es_admin(request.user):
            return Response({"details": "Acción denegada. Solo administradores."}, status=403)

        evento = get_object_or_404(Evento, id=request.data["id"])
        
        # Actualización de campos
        evento.nombre_evento = request.data.get("nombre_evento", evento.nombre_evento)
        evento.descripcion = request.data.get("descripcion", evento.descripcion)
        evento.categoria = request.data.get("categoria", evento.categoria)
        # evento.organizador = ... (Generalmente no se cambia el organizador al editar)
        evento.lugar = request.data.get("lugar", evento.lugar)
        evento.modalidad = request.data.get("modalidad", evento.modalidad)
        evento.fecha_evento = request.data.get("fecha_evento", evento.fecha_evento)
        evento.hora_inicio = request.data.get("hora_inicio", evento.hora_inicio)
        evento.hora_fin = request.data.get("hora_fin", evento.hora_fin)
        evento.cupo = request.data.get("cupo", evento.cupo)
        
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
        # Estadísticas
        total_eventos = Evento.objects.count()
        total_categorias = Categoria.objects.count()
        
        categoria_top = Evento.objects.values('categoria') \
                             .annotate(total=Count('id')) \
                             .order_by('-total') \
                             .first()

        nombre_mas_usada = "Sin datos"
        if categoria_top:
            nombre_mas_usada = categoria_top['categoria']

        return Response({
            'Total eventos': total_eventos,
            'Total categorias': total_categorias,
            'Categoria mas usada': nombre_mas_usada
        }, 200)