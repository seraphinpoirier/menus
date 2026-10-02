# menus
Générateur de menus pour la semaine. Outil multi-utilisateurs qui permet de générer des menus selon ses préférences et contraintes.

# Architecture
## Stack technique
- base de données : sqlite3 (suffisant dans un premier temps)
- backend : django
- frontend : Bootstrap + React

## Démarrage local

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Ouvrir `http://127.0.0.1:8000/`.

## Fonctionnalités actuelles

- Accueil avec le bouton « Commencer ».
- Génération de sept jours de repas, avec un repas différent le midi et le soir.
- Base SQLite contenant 20 repas initiaux limités à leur nom.
- Écran de connexion visuel, sans authentification implémentée.

## Tests

```powershell
python manage.py test
```
