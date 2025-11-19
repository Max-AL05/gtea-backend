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