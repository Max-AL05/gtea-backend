from django.db import models # type: ignore
from django.db.models.signals import post_save # type: ignore
from django.dispatch import receiver # type: ignore
from rest_framework.authentication import TokenAuthentication # type: ignore
from django.contrib.auth.models import AbstractUser, User # type: ignore
from django.conf import settings # type: ignore

class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"

class Administradores(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
# Campos específicos del perfil
    telefono = models.CharField(max_length=255, null=True, blank=True) 
    biografia = models.TextField(null=True, blank=True)

def __str__(self):
    return "Perfil del admin "+self.first_name+" "+self.last_name
    
#TODO:

class Estudiantes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    
    # --- Campos Específicos (Reducidos) ---
    telefono = models.CharField(max_length=255, null=True, blank=True)
    biografia = models.TextField(null=True, blank=True)
    # Agregamos campo de imagen para soportar la funcionalidad de editar foto
    #imagen = models.ImageField(upload_to='perfil_estudiantes/', null=True, blank=True)

    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

def __str__(self):
    return "Perfil del estudiante "+self.first_name+" "+self.last_name
    
class Organizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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

class Categoria(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "El nombre de la categoria es "+self.nombre_categoria

class Evento(models.Model):
    id = models.BigAutoField(primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')
    nombre_evento = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=255, null=True, blank=True)
    organizador = models.CharField(max_length=255, null=True, blank=True)
    lugar = models.CharField(max_length=255)
    modalidad = models.CharField(max_length=255, null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    cupo = models.PositiveIntegerField(null=True, blank=True)

    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "El nombre del evento es "+self.nombre_evento
    
#definir categoria y sedes
#llave forania y llave primaria de classEvento
