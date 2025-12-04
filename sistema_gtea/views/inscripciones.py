from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from sistema_gtea.models import Inscripcion, Evento, Estudiantes, Sede
from django.db.models import Sum, Count
from sistema_gtea.serializers import InscripcionSerializer
from django.contrib.auth.models import Group, User

def es_admin_o_organizador(user):
    return user.is_authenticated and user.groups.filter(name__in=['Administrador', 'Organizador']).exists()

def es_estudiante(user):
    return user.is_authenticated and user.groups.filter(name='Estudiante').exists()

class InscripcionesAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        
        if es_admin_o_organizador(user):
            inscripciones = Inscripcion.objects.all().order_by("-id")
        
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

    def get(self, request, *args, **kwargs):
        inscripcion = get_object_or_404(Inscripcion, id=request.GET.get("id"))
        
        if es_estudiante(request.user):
            if inscripcion.estudiante.user != request.user:
                return Response({"details": "No tienes permiso para ver esta inscripción"}, 403)
                
        serializer = InscripcionSerializer(inscripcion)
        return Response(serializer.data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not es_estudiante(request.user):
            return Response({"details": "Solo los estudiantes pueden inscribirse."}, 403)

        evento_id = request.data.get("evento")
        evento = get_object_or_404(Evento, id=evento_id)
        estudiante = get_object_or_404(Estudiantes, user=request.user)

        if Inscripcion.objects.filter(estudiante=estudiante, evento=evento, estado='inscrito').exists():
            return Response({"details": "Ya estás inscrito en este evento."}, 400)

        inscritos_actuales = Inscripcion.objects.filter(evento=evento, estado='inscrito').count()
        if inscritos_actuales >= evento.cupo:
            return Response({"details": "El evento no tiene cupo disponible."}, 400)

        inscripcion = Inscripcion.objects.create(
            estudiante=estudiante,
            evento=evento,
            estado='inscrito',
            asistencia='pendiente'
        )
        
        return Response({"inscripcion_id": inscripcion.id, "message": "Inscripción exitosa"}, 201)

class InscripcionViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        inscripcion = get_object_or_404(Inscripcion, id=request.data.get("id"))
        user = request.user

        if es_estudiante(user):
            if inscripcion.estudiante.user != user:
                return Response({"details": "No puedes modificar una inscripción ajena"}, 403)
            
            if request.data.get("estado") == "cancelado_usuario":
                inscripcion.estado = "cancelado_usuario"
                inscripcion.motivo_cancelacion = request.data.get("motivo_cancelacion", "Sin motivo especificado")
                inscripcion.save()
                return Response({"message": "Inscripción cancelada correctamente"}, 200)
            else:
                return Response({"details": "Los estudiantes solo pueden cancelar inscripciones"}, 400)

        if es_admin_o_organizador(user):
            inscripcion.estado = request.data.get("estado", inscripcion.estado)
            inscripcion.asistencia = request.data.get("asistencia", inscripcion.asistencia)
            inscripcion.motivo_cancelacion = request.data.get("motivo_cancelacion", inscripcion.motivo_cancelacion)
            
            inscripcion.save()
            return Response(InscripcionSerializer(inscripcion).data, 200)

        return Response({"details": "Permisos insuficientes"}, 403)

    def get(self, request, *args, **kwargs):
        total_eventos = Evento.objects.count()
        total_usuarios_activos = User.objects.filter(is_active=True).count()
        total_inscripciones = Inscripcion.objects.count()
        total_asistieron = Inscripcion.objects.filter(asistencia='asistio').count()
        
        tasa_asistencia = 0
        if total_inscripciones > 0:
            tasa_asistencia = (total_asistieron / total_inscripciones) * 100
            tasa_asistencia = round(tasa_asistencia, 2)

        return Response({
            'total_eventos': total_eventos,
            'usuarios_activos': total_usuarios_activos,
            'total_inscripciones': total_inscripciones,
            'tasa_asistencia_porcentaje': tasa_asistencia
        }, 200)