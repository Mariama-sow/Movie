from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('film/<uuid:film_uid>/critique/add/', views.CritiqueCreateView.as_view(), name='add_critique'),
    path('critique/<uuid:uid>/edit/', views.CritiqueUpdateView.as_view(), name='edit_critique'),
    path('critique/<uuid:uid>/delete/', views.CritiqueDeleteView.as_view(), name='delete_critique'),
]
