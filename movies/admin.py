from django.contrib import admin
from .models import Movie, Rating, Favorite

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'years', 'star', 'view_count')
    search_fields = ('title', 'director_description', 'leader')
    list_filter = ('years', 'country')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score', 'timestamp')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'timestamp')
