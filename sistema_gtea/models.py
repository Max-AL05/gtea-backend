from django.db import models # type: ignore
from django.db.models.signals import post_save # type: ignore
from django.dispatch import receiver # type: ignore
from rest_framework.authentication import TokenAuthentication # type: ignore
from django.contrib.auth.models import AbstractUser, User # type: ignore
from django.conf import settings # type: ignore

class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"

class Administradores(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
'''
    telefono = models.CharField(max_length=255, null=True, blank=True) 
    biografia = models.TextField(null=True, blank=True)
'''
def __str__(self):
    return "Perfil del admin "+self.first_name+" "+self.last_name
    
#TODO:

class Estudiantes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # <--- Falta esto
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
'''
    telefono = models.CharField(max_length=255, null=True, blank=True) 
    biografia = models.TextField(null=True, blank=True)
'''
def __str__(self):
    return "Perfil del estudiante "+self.first_name+" "+self.last_name
    
class Organizador(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True) 
    biografia = models.TextField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
'''
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
'''
def __str__(self):
    return "Perfil del organizador "+self.first_name+" "+self.last_name


class Evento(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre_evento = models.CharField(max_length=255)
    tipo_evento = models.CharField(max_length=255)
    fecha_evento = models.DateTimeField(null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_final = models.TimeField(null=True, blank=True)
    lugar = models.CharField(max_length=255)
    publico_json = models.TextField(null=True, blank=True)
    programa_educativo = models.CharField(max_length=255, null=True, blank=True)
    responsable_evento = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField()
    cupo = models.PositiveIntegerField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "El nombre del evento es "+self.nombre_evento
    
#definir categoria y sedes
#llave forania y llave priaria de classEvento