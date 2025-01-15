from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-controlform-control-lg rounded-3', 'placeholder': 'Votre adresse email'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg rounded-3', 'placeholder': 'Votre mot de passe'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        # Extraire 'request' des kwargs, s'il est passé
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        # Authentification avec email
        user = authenticate(email=email, password=password)
        if not user:
            raise forms.ValidationError("Connexion invalide.")
        
        # Stocker l'utilisateur pour une utilisation ultérieure
        self.user = user
        return cleaned_data

    def get_user(self):
        return self.user

    

class CustomUserCreateForm(forms.ModelForm):
    password = forms.CharField(
          widget=forms.PasswordInput(attrs={'class': 'form-control ','placeholder' : 'votre mot de passe',}), min_length=8
           
            )
    password_confirm = forms.CharField(
          widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'mot de passe de confirmation'})
           
           )
    email = forms.EmailField(
          required=True,
          help_text= 'Veuillez entrer une adresse email valide',
          widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre adresse email'})

           )
    last_name = forms.CharField(
          required=True, max_length=30,
          widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Votre nom'})

           )
    first_name = forms.CharField(
          max_length=30, required=True,
          widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Votre prenom'})
            
           )
    avatar = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))
    class Meta:
        model = CustomUser
        fields = ('last_name','first_name','username','email','password','password_confirm','avatar')
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prenom'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom_utilisateur'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control','placeholder': 'Votre image profil'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)  # Applique les règles de validation de Django
        return password
        

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hacher le mot de passe
        if commit:
            user.save()
        return user
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email existe deja.")
        return email


# forms.py - Mise à jour des widgets
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg rounded-3',
            'placeholder': 'Votre adresse email'
        }),
        label="Email"
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Aucun compte n'est associé à cette adresse email.")
        return email

class PasswordResetConfirmForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg rounded-3',
            'placeholder': 'Nouveau mot de passe'
        }),
        min_length=8
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg rounded-3',
            'placeholder': 'Confirmer le nouveau mot de passe'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")
            validate_password(password)
        return cleaned_data