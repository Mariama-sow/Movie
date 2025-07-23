import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from functools import lru_cache  # Pour implémenter un cache en mémoire
import logging
logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')  # Charge explicitement depuis la racine


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class TMDBServices:
    BASE_URL = "https://api.themoviedb.org/3"
    
    # Définition de l'API_KEY comme variable de classe
    API_KEY = os.getenv('TMDB_API_KEY')
    
    if not API_KEY:
        raise ValueError(
            "Configuration manquante : TMDB_API_KEY doit être définie dans .env\n"
            f"Chemin recherché : {BASE_DIR / '.env'}"
        )

    @classmethod
    @lru_cache(maxsize=100)
    def get_movie_details(cls, tmdb_id):
        """Récupère les détails d'un film via son ID TMDB."""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/movie/{tmdb_id}",
                params={
                    'api_key': cls.API_KEY,  # Utilisation de l'attribut de classe
                    'language': 'fr-FR',
                    'append_to_response': 'credits,videos'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur TMDB: {str(e)}")
            return {"error": str(e)}

    @classmethod
    @lru_cache(maxsize=100)
    def search_movie(cls, query):
        """Recherche des films via l'API TMDB."""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/search/movie",
                params={
                    'api_key': cls.API_KEY,
                    'query': query,
                    'language': 'fr-FR'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur TMDB: {str(e)}")
            return {"error": str(e)}
        
    @classmethod
    @lru_cache(maxsize=100)  # Cache également pour limiter les requêtes
    def get_movie_details(cls, tmdb_id):
        """Récupère les détails d'un film via son ID TMDB."""
        if not tmdb_id:
            return {"error": "L'identifiant du film est manquant."}

        try:
            response = requests.get(
                f"{cls.BASE_URL}/movie/{tmdb_id}",
                params={
                    'api_key': cls.API_KEY,
                    'language': 'fr-FR'
                }
            )
            response.raise_for_status()  # Lève une exception si le statut HTTP est une erreur
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Une erreur est survenue lors de la récupération des détails : {str(e)}"}
