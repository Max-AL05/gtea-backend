from django.shortcuts import render # type: ignore
from django.db.models import * # type: ignore
from django.db import transaction # type: ignore
from sistema_gtea.serializers import *
from sistema_gtea.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication # type: ignore
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView # type: ignore
from rest_framework import permissions # type: ignore
from rest_framework import generics # type: ignore
from rest_framework import status # type: ignore
from rest_framework.authtoken.views import ObtainAuthToken # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.decorators import api_view # type: ignore
from rest_framework.reverse import reverse # type: ignore
from rest_framework import viewsets # type: ignore
from django.shortcuts import get_object_or_404 # type: ignore
from django.core import serializers # type: ignore
from django.utils.html import strip_tags # type: ignore
from django.contrib.auth import authenticate, login # type: ignore
from django.contrib.auth.models import Group # type: ignore
from django.contrib.auth import get_user_model # type: ignore
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from django_filters import rest_framework as filters # type: ignore
from datetime import datetime
from django.conf import settings # type: ignore
from django.template.loader import render_to_string # type: ignore
import string
import random
import json


class EventosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        eventos = Evento.objects.all().order_by("id")
        eventos = EventoSerializer(eventos, many=True).data
        if not eventos:
            return Response({}, 400)
        for evento in eventos:
            evento["publico_json"] = json.loads(evento["publico_json"])
        return Response(eventos, 200)

class EventoView(generics.CreateAPIView):
    # permission_classes = (permissions.IsAuthenticated,)

    # Obtener evento por ID
    def get(self, request, *args, **kwargs):
        evento = get_object_or_404(Evento, id=request.GET.get("id"))
        evento = EventoSerializer(evento, many=False).data
        evento["publico_json"] = json.loads(evento["publico_json"])
        return Response(evento, 200)

    # Registrar nuevo evento
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["publico_json"] = json.dumps(data["publico_json"])

        evento = EventoSerializer(data=data)
        if evento.is_valid():
            evento = evento.save()
            return Response({"evento_created_id": evento.id}, 201)
        return Response(evento.errors, status=status.HTTP_400_BAD_REQUEST)

#editar evento
class EventosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
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
        evento.save()
        user = EventoSerializer(evento, many=False).data

        return Response(user,200)
    
    #Eliminar evento
    def delete(self, request, *args, **kwargs):
        evento = get_object_or_404(Evento, id=request.GET.get("id"))
        try:
            evento.delete()
            return Response({"details":"Evento eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

