from django.contrib import admin # type: ignore
from sistema_gtea.models import *

admin.site.register(Administradores)
admin.site.register(Estudiantes)
admin.site.register(Organizador)

admin.site.register(Evento)