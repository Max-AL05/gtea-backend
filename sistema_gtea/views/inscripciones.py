from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from sistema_gtea.models import Inscripcion, Evento, Estudiantes
from sistema_gtea.serializers import InscripcionSerializer

# Helpers de permisos
def es_admin_o_organizador(user):
    return user.is_authenticated and user.groups.filter(name__in=['Administrador', 'Organizador']).exists()

def es_estudiante(user):
    return user.is_authenticated and user.groups.filter(name='Estudiante').exists()

class InscripcionesAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Si es Admin u Organizador, ve TODAS las inscripciones
        if es_admin_o_organizador(user):
            inscripciones = Inscripcion.objects.all().order_by("-id")
        
        # Si es Estudiante, solo ve SUS inscripciones
        elif es_estudiante(user):
            try:
                perfil = Estudiantes.objects.get(user=user)
                inscripciones = Inscripcion.objects.filter(estudiante=perfil).order_by("-id")
            except Estudiantes.DoesNotExist:
                return Response({"details": "Perfil de estudiante no encontrado"}, 400)
        else:
            return Response([], 200)

        data = InscripcionSerializer(inscripciones, many=True).data
        return Response(data, 200)

class InscripcionView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # GET: Ver detalle de una inscripción
    def get(self, request, *args, **kwargs):
        inscripcion = get_object_or_404(Inscripcion, id=request.GET.get("id"))
        
        # Validar que el estudiante solo vea la suya
        if es_estudiante(request.user):
            if inscripcion.estudiante.user != request.user:
                return Response({"details": "No tienes permiso para ver esta inscripción"}, 403)
                
        serializer = InscripcionSerializer(inscripcion)
        return Response(serializer.data, 200)

    # POST: Inscribirse a un evento (Solo Estudiantes)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not es_estudiante(request.user):
            return Response({"details": "Solo los estudiantes pueden inscribirse."}, 403)

        evento_id = request.data.get("evento")
        evento = get_object_or_404(Evento, id=evento_id)
        estudiante = get_object_or_404(Estudiantes, user=request.user)

        # 1. Validar si ya está inscrito (y no está cancelado)
        if Inscripcion.objects.filter(estudiante=estudiante, evento=evento, estado='inscrito').exists():
            return Response({"details": "Ya estás inscrito en este evento."}, 400)

        # 2. Validar Cupo Disponible
        inscritos_actuales = Inscripcion.objects.filter(evento=evento, estado='inscrito').count()
        if inscritos_actuales >= evento.cupo:
            return Response({"details": "El evento no tiene cupo disponible."}, 400)

        # 3. Crear Inscripción
        inscripcion = Inscripcion.objects.create(
            estudiante=estudiante,
            evento=evento,
            estado='inscrito',
            asistencia='pendiente'
        )
        
        return Response({"inscripcion_id": inscripcion.id, "message": "Inscripción exitosa"}, 201)

class InscripcionViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    # PUT: Cancelar o Tomar Asistencia
    def put(self, request, *args, **kwargs):
        inscripcion = get_object_or_404(Inscripcion, id=request.data.get("id")) # Usa .get aqui tambien por seguridad
        user = request.user

        # Lógica para ESTUDIANTE (Solo puede cancelar)
        if es_estudiante(user):
            if inscripcion.estudiante.user != user:
                return Response({"details": "No puedes modificar una inscripción ajena"}, 403)
            
            # Solo permitimos cambiar el estado a cancelado
            if request.data.get("estado") == "cancelado_usuario":
                inscripcion.estado = "cancelado_usuario"
                inscripcion.motivo_cancelacion = request.data.get("motivo_cancelacion", "Sin motivo especificado")
                inscripcion.save()
                return Response({"message": "Inscripción cancelada correctamente"}, 200)
            else:
                return Response({"details": "Los estudiantes solo pueden cancelar inscripciones"}, 400)

        # Lógica para ADMIN / ORGANIZADOR (Control total)
        if es_admin_o_organizador(user):
            # CORRECCIÓN AQUÍ: Agregamos .get()
            inscripcion.estado = request.data.get("estado", inscripcion.estado)
            inscripcion.asistencia = request.data.get("asistencia", inscripcion.asistencia)
            inscripcion.motivo_cancelacion = request.data.get("motivo_cancelacion", inscripcion.motivo_cancelacion)
            
            inscripcion.save()
            return Response(InscripcionSerializer(inscripcion).data, 200)

        return Response({"details": "Permisos insuficientes"}, 403)