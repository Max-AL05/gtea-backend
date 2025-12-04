from rest_framework import serializers # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from sistema_gtea.models import *
#actualizado
class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    telefono = serializers.CharField(required=False, allow_blank=True)
    biografia = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email', 'telefono', 'biografia')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'

class Estudianteserializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Estudiantes
        fields = '__all__'

class OrganizadorSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Organizador
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'

    # ESTA FUNCIÓN ES LA SOLUCIÓN:
    # Se ejecuta justo antes de enviar la respuesta al usuario (GET)
    # Sobrescribe el campo 'organizador' para mostrar el nombre en vez del ID.
    def to_representation(self, instance):
        # 1. Obtiene la representación original (donde 'organizador' es un ID)
        response = super().to_representation(instance)
        
        # 2. Busca los datos del usuario real y reemplaza el ID por el Nombre
        if instance.organizador and instance.organizador.user:
            full_name = f"{instance.organizador.user.first_name} {instance.organizador.user.last_name}"
            response['organizador'] = full_name  # ¡Aquí ocurre el cambio visual!
        
        return response

class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = '__all__'

class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = '__all__'