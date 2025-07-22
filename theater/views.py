from django.shortcuts import render , get_object_or_404 , redirect
from django.urls import reverse 
from django.core.paginator import Paginator
from itertools import chain
from django.views.generic import ListView , DetailView
from django.db.models import Q , Avg ,Count
from django.contrib import messages
from review.models import Critique
from review.forms import CommentaireForm
from services.tmdb import TMDBServices
from users.models import CustomUser
from .models import Film
from .forms import FilmFilterForm , SearchForm
  

def home(request):
    # Films avec au moins une critique, triés par popularité
    popular_films = Film.objects.annotate(
        avg_rating=Avg('critique__note'),
        review_count=Count('critique')
    ).filter(review_count__gte=1).order_by('-avg_rating')[:4]
    
    # Si aucun film avec critique, prendre les 4 derniers films
    if not popular_films.exists():
        popular_films = Film.objects.order_by('-date_sortie')[:4]

    # Dernières critiques
    recent_critiques = Critique.objects.select_related(
        'film', 'utilisateur'
    ).order_by('-date_publication')[:3]

    context = {
        'films': popular_films,
        'recent_critiques': recent_critiques,
        'total_films': Film.objects.count(),
        'total_critiques': Critique.objects.count(),
        'total_users': CustomUser.objects.count(),
    }
    return render(request, 'theater/home.html', context)


class FilmListView(ListView):
    model = Film
    template_name = 'theater/film.html'
    context_object_name = 'films'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        filters = {
            'genre': self.request.GET.get('genre'),
            'annee': self.request.GET.get('annee'),
            'note_min': self.request.GET.get('note_min')
        }

        # Filtrage des films locaux
        local_films = Film.objects.all()
        
        if query:
            local_films = local_films.filter(Q(titre__icontains=query) | Q(synopsis__icontains=query))
        
        if filters['genre']:
            local_films = local_films.filter(genre=filters['genre'])
        
        if filters['annee']:
            local_films = local_films.filter(date_sortie__year=filters['annee'])
        
        if filters['note_min']:
            local_films = local_films.annotate(avg_rating=Avg('critique__note'))\
                                   .filter(avg_rating__gte=filters['note_min'])

        # Recherche TMDB (uniquement si query existe mais pas de filtres actifs)
        tmdb_results = []
        if query and not any(filters.values()):
            tmdb_results = TMDBServices.search_movie(query).get('results', [])
            tmdb_films = [{
                'id': r['id'],
                'titre': r['title'],
                'synopsis': r['overview'],
                'affiche': f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r['poster_path'] else None,
                'note_moyenne': r['vote_average'],
                'duree': r.get('runtime', 0),
                'date_sortie': r['release_date'],
                'is_tmdb': True  # Marqueur pour les films TMDB
            } for r in tmdb_results]

            # Fusion des résultats
            combined_results = list(chain(local_films, tmdb_films))
        else:
            combined_results = list(local_films)

        paginator = Paginator(combined_results, self.paginate_by)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilmFilterForm(self.request.GET or None)
        context['search_form'] = SearchForm(
            initial={'query': self.request.GET.get('query', '')}
        )
        return context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['films'] = self.get_queryset()
        context['is_paginated'] = True
        context['page_obj'] = context['films']
        context['form'] = FilmFilterForm(self.request.GET or None)
        context['search_form'] = SearchForm(
            initial={'query': self.request.GET.get('query', '')}
        )
        return context


class FilmDetailView(DetailView):
    model = Film
    template_name = 'theater/film_detail.html'
    context_object_name = 'film'
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentaireForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        critique_id = request.POST.get('critique_id')
        if not critique_id:
            messages.error(request, 'Erreur lors de l\'ajout du commentaire')
            return redirect('theater:film_detail', uid=self.object.uid)
            
        critique = get_object_or_404(Critique, id=critique_id)
        form = CommentaireForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            commentaire = form.save(commit=False)
            commentaire.critique = critique
            commentaire.utilisateur = request.user
            commentaire.save()
            messages.success(request, 'Commentaire ajouté')
            
        return redirect('theater:film_detail', uid=self.object.uid)

    def get_success_url(self):
         return reverse('theater:film_detail', kwargs={'uid': self.object.uid})
    

def film_detail_tmdb(request, tmdb_id):
    # Récupére les détails du film depuis TMDB
    film_details = TMDBServices.get_movie_details(tmdb_id)
    
    if film_details:
        film = {
            'id': film_details['id'],
            'titre': film_details['title'],
            'synopsis': film_details['overview'],
            'affiche': f"https://image.tmdb.org/t/p/w500{film_details['poster_path']}" if film_details['poster_path'] else None,
            'note_moyenne': film_details['vote_average'],
            'duree': film_details.get('runtime', 0),
            'date_sortie': film_details['release_date'],
            'genres': [genre['name'] for genre in film_details.get('genres', [])],
            
        }
        return render(request, 'theater/film_detail_tmdb.html', {'film': film})
    else:
        messages.error(request, "Film non trouvé")
        return redirect('theater:film_list')