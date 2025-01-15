import uuid
from django.db import models
from theater.models import Film
from users.models import CustomUser


class Critique(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    titre = models.CharField(max_length=255)
    texte = models.TextField()
    note = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    date_publication = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('film', 'utilisateur')  # Un utilisateur ne peut écrire qu'une critique par film

    def __str__(self):
        return f"{self.titre} - {self.film.titre}"



class Commentaire(models.Model):
    critique = models.ForeignKey(Critique, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    texte = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.utilisateur.username} sur {self.critique.titre}"
