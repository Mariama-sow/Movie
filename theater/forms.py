from django import forms
from .models import Film , Contact

class FilmFilterForm(forms.Form):
    RATING_CHOICES = [
        ('', 'Toutes les notes'),
        (4, '4+ étoiles'),
        (3, '3+ étoiles'),
        (2, '2+ étoiles'),
        (1, '1+ étoile'),
    ]
    
    genre = forms.ChoiceField(
        choices=[('', 'Tous les genres')],  
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    annee = forms.ChoiceField(
        choices=[('', 'Toutes les années')],  
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    note_min = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Note minimum'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Récupérer tous les genres uniques
        genres = Film.objects.values_list('genre', flat=True).distinct()
        self.fields['genre'].choices += [(g, g) for g in genres]
        
        
        annees = Film.objects.dates('date_sortie', 'year')
        self.fields['annee'].choices += [(date.year, date.year) for date in annees]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['your_name', 'email', 'subject', 'message']
        widgets = {
            'your_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Votre message'}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un film...'
        })
    )