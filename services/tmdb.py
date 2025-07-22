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

class TMDBServices:
    BASE_URL = "https://api.themoviedb.org/3"
    
    @classmethod
    def get_api_key(cls):
        """Charge la clé API avec gestion d'erreur améliorée"""
        api_key = os.getenv('TMDB_API_KEY')
        if not api_key:
            logger.error("Clé API TMDB non trouvée. Vérifiez votre fichier .env")
            raise ValueError(
                "Configuration manquante : TMDB_API_KEY doit être définie dans .env\n"
                f"Chemin recherché : {BASE_DIR / '.env'}"
            )
        return api_key

    @classmethod
    @lru_cache(maxsize=100)
    def search_movie(cls, query):
        """Recherche de films avec gestion robuste des erreurs"""
        try:
            response = requests.get(
                f"{cls.BASE_URL}/search/movie",
                params={
                    'api_key': cls.get_api_key(),  # Appel sécurisé
                    'query': query,
                    'language': 'fr-FR'
                },
                timeout=10  # Timeout explicite
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(f"Erreur TMDB: {str(e)}")
            return {"error": "Service indisponible"}
        
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
