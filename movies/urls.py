from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, RatingViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]
