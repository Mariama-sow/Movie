from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email=email)
        extra_fields.setdefault('username', None)  # Définir username sur None
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Assurer qu'un username est défini pour le superuser
        if 'username' not in extra_fields:
            # Utiliser la partie locale de l'email comme username par défaut
            extra_fields['username'] = email.split('@')[0]
        
        return self.create_user(email, password, **extra_fields)
