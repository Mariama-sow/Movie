from rest_framework import serializers
from review.models import Critique
from theater.models import Film
from users.models import CustomUser

class CustomUserSerialisers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('firstname','lastname','username','email')
        read_only_fields = fields

class CritiqueSerialisers(serializers.ModelSerializer):
    class Meta:
        model = Critique
        fields = '__all__'

class FilmSerialisers(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'