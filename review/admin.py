from django.contrib import admin
from .models import Critique, Commentaire

@admin.register(Critique)
class CritiqueAdmin(admin.ModelAdmin):
    list_display = ['titre', 'film', 'utilisateur', 'note', 'date_publication']
    list_filter = ['note', 'date_publication']
    search_fields = ['titre', 'texte', 'film__titre', 'utilisateur__username']

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['critique', 'utilisateur', 'date_publication']
    list_filter = ['date_publication']
    search_fields = ['texte', 'utilisateur__username']
