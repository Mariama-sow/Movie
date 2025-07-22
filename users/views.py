from django.shortcuts import render , redirect
from django.contrib.auth.views import LoginView , LogoutView
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView , UpdateView
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .forms import CustomUserCreateForm ,CustomUserLoginForm , UserProfileUpdateForm , PasswordResetConfirmForm, PasswordResetRequestForm
from .models import CustomUser

import logging

logger = logging.getLogger(__name__)



class CustomLoginView(LoginView):
    authentication_form = CustomUserLoginForm
    template_name = 'users/login.html'
    
    def form_valid(self,form):
        messages.success(self.request,"connexion réussie !")
        return super().form_valid(form)
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Passer 'request' au formulaire
        return kwargs
    
    def form_invalid(self, form):
        logger.error("Le formulaire est invalide : %s", form.errors)  
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy ('theater:home')


class CustomCreateUserView(CreateView):
    model = CustomUser
    form_class = CustomUserCreateForm
    template_name = 'users/Create.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        with transaction.atomic():
            user = form.save()
            self.send_welcome_email(user)
        messages.success(self.request, "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.")
        return redirect(self.success_url)

    def send_welcome_email(self, user):
        try:
            subject = "Bienvenue sur notre plateforme"
            message = (
                f"Bonjour {user.first_name},\n\n"
                "Merci de vous être inscrit(e) sur notre plateforme. "
                "Nous sommes ravis de vous compter parmi nous.\n\n"
                "Bonne journée !"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            logger.error("Erreur lors de l'envoi de l'email de bienvenue : %s", e)

    
class LogoutView(View):
    login_url = reverse_lazy('users:login') 

    def get(self,request) :
        logout(request) 
        messages.success(
            self.request,
            "Votre a ete deconnecte"
        )
        return redirect(self.login_url)   
    

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour avec succès!")
        return super().form_valid(form)
    


class PasswordResetRequestView(View):
    template_name = 'users/password_reset_request.html'
    form_class = PasswordResetRequestForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Construction du lien de réinitialisation
            reset_url = request.build_absolute_uri(
                reverse_lazy('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            
            subject = "Réinitialisation de votre mot de passe"
            email_template = 'users/password_reset_email.html'
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'Votre Site'
            }
            email_content = render_to_string(email_template, context)
            
            try:
                send_mail(
                    subject,
                    email_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=email_content
                )
                messages.success(request, 
                    "Un email contenant les instructions de réinitialisation a été envoyé."
                )
                return redirect('users:login')
            except Exception as e:
                logger.error(f"Erreur d'envoi d'email: {e}")
                messages.error(request, 
                    "Une erreur s'est produite lors de l'envoi de l'email."
                )
                
        return render(request, self.template_name, {'form': form})

class PasswordResetConfirmView(View):
    template_name = 'users/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                return render(request, self.template_name, {'form': self.form_class()})
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        
        messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
        return redirect('users:login')

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        form = self.form_class(request.POST)
        if user and default_token_generator.check_token(user, token) and form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
            return redirect('users:login')
        
        messages.error(request, "La réinitialisation du mot de passe a échoué.")
        return render(request, self.template_name, {'form': form})