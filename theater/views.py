from django.shortcuts import render , get_object_or_404 , redirect
from django.urls import reverse 
from django.core.paginator import Paginator
from itertools import chain
from django.views.generic import ListView , DetailView
from django.db.models import Q
from django.contrib import messages
from review.models import Critique
from review.forms import CommentaireForm
from services.tmdb import TMDBServices
from .models import Film
from .forms import FilmFilterForm , SearchForm



def home(request):
    return render(request,'theater/home.html')


class FilmListView(ListView):
    model = Film
    template_name = 'theater/film.html'
    context_object_name = 'films'
    paginate_by = 12  # Pagination optionnelle

    def get_queryset(self):
        # query = self.request.GET.get('query', '')
        # queryset = Film.objects.all()
        
        # # Recherche les films
        # if query:
        #     # Recherche locale
        #     local_results = Film.objects.filter(
        #         Q(titre__icontains=query) |
        #         Q(synopsis__icontains=query)
        #     )
            
        #     # Recherche TMDB
        #     tmdb_results = TMDBServices.search_movie(query)
        #       # Convertir les résultats TMDB en un format compatible
        #     tmdb_films = [
        #         Film(
        #             titre=tmdb_result['title'],
        #             synopsis=tmdb_result['overview'],
        #             affiche=tmdb_result['poster_path'],
        #             note_moyenne=tmdb_result['vote_average'],
        #             duree=tmdb_result.get('runtime', 0),  # Si la durée est disponible
        #             date_sortie=tmdb_result['release_date']
        #         )
        #         for tmdb_result in tmdb_results.get('results', [])
        #     ]
                
        #     # Fusionner les résultats locaux et TMDB
        #     queryset = chain(local_results, tmdb_films)
        
        # # Récupérer les paramètres de filtrage
        # genre = self.request.GET.get('genre')
        # annee = self.request.GET.get('annee')
        # note_min = self.request.GET.get('note_min')

        # # Appliquer les filtres
        # if genre:
        #     queryset = queryset.filter(genre=genre)
        # if annee:
        #     queryset = queryset.filter(date_sortie__year=annee)
        # if note_min:
        #     queryset = queryset.filter(note_moyenne__gte=float(note_min))

        # return queryset

        query = self.request.GET.get('query', '')
        local_results = Film.objects.filter(Q(titre__icontains=query) | Q(synopsis__icontains=query)) if query else Film.objects.all()
        tmdb_results = TMDBServices.search_movie(query).get('results', []) if query else []

          # Transformer les résultats TMDB en objets compatibles
        tmdb_films = [
        {
            'id': tmdb_result['id'],  # Ajout de l'ID TMDB
            'titre': tmdb_result['title'],
            'synopsis': tmdb_result['overview'],
            'affiche': f"https://image.tmdb.org/t/p/w500{tmdb_result['poster_path']}" if tmdb_result['poster_path'] else None,
            'note_moyenne': tmdb_result['vote_average'],
            'duree': tmdb_result.get('runtime', 0),
            'date_sortie': tmdb_result['release_date']
        }
        for tmdb_result in tmdb_results
        ]
         # Fusionner les résultats locaux et TMDB
        combined_results = list(chain(local_results, tmdb_films))

        # Ajouter la pagination
        paginator = Paginator(combined_results, self.paginate_by)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)

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
    # Récupérer les détails du film depuis TMDB
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
            # Ajoutez d'autres champs selon vos besoins
        }
        return render(request, 'theater/film_detail_tmdb.html', {'film': film})
    else:
        messages.error(request, "Film non trouvé")
        return redirect('theater:film_list')