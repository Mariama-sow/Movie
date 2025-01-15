from django import forms
from .models import Critique, Commentaire

class CritiqueForm(forms.ModelForm):
    class Meta:
        model = Critique
        fields = ['titre', 'texte', 'note']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'texte': forms.Textarea(attrs={'class': 'form-control'}),
            'note': forms.Select(attrs={'class': 'form-control'})
        }

class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['texte']
        widgets = {
            'texte': forms.TextInput(attrs={'class': 'form-control'})
        }

    