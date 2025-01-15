from django.urls import path
from rest_framework import routers
from .views import(FilmViewset, CritiqueViewset)

app_name = 'api'

router = routers.SimpleRouter()
router.register('films', FilmViewset)
router.register('critique',CritiqueViewset)


urlpatterns = router.urls

