from rest_framework import serializers # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from sistema_gtea.models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

#actualizado
class AdminSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=True)
    last_name = serializers.CharField(source='user.last_name', required=True)
    email = serializers.EmailField(source='user.email', read_only=True)  

    class Meta:
        model = Administradores
        fields = ['first_name', 'last_name', 'email', 'telefono', 'biografia']
        read_only_fields = ['email'] 

    def update(self, instance, validated_data):
        # Actualizar datos
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.biografia = validated_data.get('biografia', instance.biografia)
        instance.save()
        
        user = instance.user
        user.first_name = validated_data.get('user', {}).get('first_name', user.first_name)
        user.last_name = validated_data.get('user', {}).get('last_name', user.last_name)
        user.save()

        return instance

class Estudianteserializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Estudiantes
        fields = '__all__'

class Organizadorerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Organizador
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'

