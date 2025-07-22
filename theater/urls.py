from django.urls import path

from .views import FilmListView, FilmDetailView ,home , film_detail_tmdb


app_name ='theater'

urlpatterns = [
    path('film/tmdb/<int:tmdb_id>/', film_detail_tmdb, name='film_detail_tmdb'),
    path('film/<uuid:uid>', FilmDetailView.as_view(), name= 'film_detail'),
    path('film/',FilmListView.as_view(),name= 'film'),
    path('',home,name= 'home'),
    
]
