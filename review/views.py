from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Critique , Film
from .forms import CritiqueForm 


class CritiqueCreateView(LoginRequiredMixin, CreateView):
    model = Critique
    form_class = CritiqueForm
    template_name = 'review/critique_form.html'
    
    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        form.instance.film = get_object_or_404(Film, uid=self.kwargs['film_uid'])
        try:

            return super().form_valid(form)    
        except IntegrityError:
            messages.error(
                self.request,
                "Vous avez déjà publié une critique pour ce film. Vous pouvez la modifier mais pas en créer une nouvelle."
            )
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('theater:film_detail', kwargs={'uid': self.kwargs['film_uid']})

class CritiqueUpdateView(LoginRequiredMixin, UpdateView):
    model = Critique
    form_class = CritiqueForm
    template_name = 'review/critique_form.html'
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_queryset(self):
        return Critique.objects.filter(utilisateur=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('theater:film_detail', kwargs={'uid': self.object.film.uid})

class CritiqueDeleteView(LoginRequiredMixin, DeleteView):
    model = Critique
    template_name = 'review/critique_confirm_delete.html'
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_queryset(self):
        return Critique.objects.filter(utilisateur=self.request.user)

    def get_success_url(self):
        return reverse_lazy('theater:film_detail', kwargs={'uid': self.object.film.uid})


