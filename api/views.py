from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import APIException
from django.core.cache import cache
from review.models import Critique
from theater.models import Film
from services.tmdb import TMDBServices
from .serializers import CritiqueSerialisers,FilmSerialisers


class CritiqueViewset(viewsets.ModelViewSet):
    queryset = Critique.objects.all()
    serializer_class = CritiqueSerialisers
    permission_classes = [IsAuthenticatedOrReadOnly]


class FilmPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'
    max_page_size = 30



class FilmViewset(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerialisers
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = FilmPagination

    @action(detail=False, methods=['get'])
    def search(self,request):
        query = request.query_params.get('q', '')

        if not query:
            return Response({"error": "Le paramètre 'q' est requis pour la recherche."}, status=400)

        cache_key = f"tmdb_serach_{query}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return  Response(cached_results)
        
        try:

            tmdb_service = TMDBServices()
            results = tmdb_service.search_movies(query)
            # Mise en cache des résultats pour 1 heure
            cache.set(cache_key,results,timeout=3600)
            return Response(results)
        
        except Exception as e:

            raise APIException(f"Erreur lors de la recherche : {str(e)}")
        
    





