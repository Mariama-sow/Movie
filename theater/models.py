import uuid
from django.db import models
from django.db.models import Avg, Count

class Acteur(models.Model):
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)  
    photo = models.ImageField(upload_to='acteurs/', blank=True, null=True)

    def __str__(self):
        return self.nom



class Film(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('fantasy', 'Fantasy'),
        ('horror', 'Horror'),

    ]

    titre = models.CharField(max_length=255 , verbose_name='Titre')
    synopsis = models.TextField(verbose_name='Synopsis')
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES , verbose_name='Genre')
    date_sortie = models.DateField(verbose_name='Date de Sortie')
    acteurs = models.ManyToManyField(Acteur, related_name='films')  
    duree = models.PositiveIntegerField(help_text="Durée du film en minutes.")
    affiche = models.ImageField(upload_to='films_affiches/')

    def __str__(self):
        return self.titre 

    def note_moyenne(self):
        return self.critique_set.aggregate(Avg('note'))['note__avg'] or 0

    def nombre_critiques(self):
        return self.critique_set.count()

    def popularite(self):
        return (self.note_moyenne() * self.nombre_critiques()) / 5



class Contact(models.Model):
    your_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()