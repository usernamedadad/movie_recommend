from rest_framework import serializers
from .models import Movie, Rating, Favorite
from django.contrib.auth.models import User

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    movie_details = MovieSerializer(source='movie', read_only=True)

    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')

class FavoriteSerializer(serializers.ModelSerializer):
    movie_details = MovieSerializer(source='movie', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'movie', 'movie_details', 'timestamp')
        read_only_fields = ('user', 'timestamp')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
