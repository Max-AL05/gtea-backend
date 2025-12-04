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

    telefono = models.CharField(max_length=255, null=True, blank=True) 
    biografia = models.TextField(null=True, blank=True)
    #imagen = models.ImageField(upload_to='perfil_admins/', null=True, blank=True)

def __str__(self):
    return "Perfil del admin "+self.first_name+" "+self.last_name
    
#TODO:

class Estudiantes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    
    telefono = models.CharField(max_length=255, null=True, blank=True)
    biografia = models.TextField(null=True, blank=True)
    #imagen = models.ImageField(upload_to='perfil_estudiantes/', null=True, blank=True)

    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

def __str__(self):
    return "Perfil del estudiante "+self.first_name+" "+self.last_name
    
class Organizador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True) 
    biografia = models.TextField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    password = models.CharField(max_length=255, null=True, blank=True)

    #imagen = models.ImageField(upload_to='perfil_estudiantes/', null=True, blank=True)

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
    nombre_evento = models.CharField(max_length=255)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=255, null=True, blank=True)
    
    # Relación original (Mantiene el ID)
    organizador = models.ForeignKey(Organizador, on_delete=models.CASCADE, null=True, blank=True, related_name='eventos')    
    
    # NUEVO CAMPO: Guardará el nombre en texto plano
    nombre_organizador = models.CharField(max_length=255, null=True, blank=True)

    lugar = models.CharField(max_length=255)
    modalidad = models.CharField(max_length=255, null=True, blank=True)
    fecha_evento = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)   
    hora_fin = models.TimeField(null=True, blank=True)
    cupo = models.PositiveIntegerField(null=True, blank=True)
    
    publico_json = models.TextField(null=True, blank=True, default="[]")
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    # LÓGICA AUTOMÁTICA: Antes de guardar, rellenamos el nombre
    def save(self, *args, **kwargs):
        if self.organizador:
            nombre = self.organizador.first_name or ""
            apellido = self.organizador.last_name or ""
            self.nombre_organizador = f"{nombre} {apellido}".strip()
        super(Evento, self).save(*args, **kwargs)

    def __str__(self):
        return "El nombre del evento es "+self.nombre_evento

class Sede(models.Model):
    id = models.BigAutoField(primary_key=True)
    edificio = models.CharField(max_length=255)
    aula = models.CharField(max_length=255)
    capacidad = models.PositiveIntegerField()
    recursos_json = models.TextField(null=True, blank=True, default="[]") 
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    #imagen = models.ImageField(upload_to='sedes/', null=True, blank=True)

    def __str__(self):
        return f"{self.edificio} - {self.aula}"

class Inscripcion(models.Model):
    id = models.BigAutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE, related_name='inscripciones')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscritos')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    ESTADOS = [
        ('inscrito', 'Inscrito'),
        ('cancelado_usuario', 'Cancelado por Usuario'),
        ('cancelado_organizador', 'Cancelado por Organizador'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADOS, default='inscrito')
    motivo_cancelacion = models.TextField(null=True, blank=True)
    ASISTENCIA = [
        ('pendiente', 'Pendiente'),
        ('asistio', 'Asistió'),
        ('no_asistio', 'No Asistió'),
    ]
    asistencia = models.CharField(max_length=20, choices=ASISTENCIA, default='pendiente')
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.estudiante} - {self.evento.nombre_evento}"