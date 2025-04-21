# App/cache.py
import requests

categories_cache = []
areas_cache = []

def preload_categories():
    global categories_cache
    if not categories_cache:
        res = requests.get('https://www.themealdb.com/api/json/v1/1/list.php?c=list')
        if res.ok:
            categories_cache = [c['strCategory'] for c in res.json().get('meals', [])]

def preload_areas():
    global areas_cache
    if not areas_cache:
        res = requests.get('https://www.themealdb.com/api/json/v1/1/list.php?a=list')
        if res.ok:
            areas_cache = [a['strArea'] for a in res.json().get('meals', [])]

def get_cached_categories():
    return categories_cache

def get_cached_areas():
    return areas_cache
