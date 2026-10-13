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
- Création de compte avec un nom d'utilisateur et un mot de passe à confirmer, puis ouverture automatique d'une session.
- Connexion avec le nom d'utilisateur et le mot de passe du compte.

### Comptes

- `/inscription/` affiche le formulaire de création de compte Django. Après une inscription valide, le compte est créé et l'utilisateur est connecté.
- `/connexion/` affiche le formulaire de connexion Django. Après une connexion valide, l'utilisateur est connecté.
- Les deux formulaires proposent un lien vers l'autre parcours. Ils conservent un paramètre `next` lorsqu'il cible le même hôte; sans destination sûre, le retour se fait à l'accueil (`/`).
- `/profil/` est réservé aux utilisateurs connectés. Il permet de modifier le nom d'utilisateur et de choisir une photo parmi les avatars fournis, puis d'enregistrer ces changements.
- Depuis le profil, `/repas/` permet de définir pour chaque repas une fréquence « Jamais », « Régulier » (par défaut) ou « Très fréquent ». Les préférences sont propres à chaque utilisateur.
- Sur la page de génération, un utilisateur connecté peut ouvrir le réglage de fréquence à côté de chaque repas. Les repas « Jamais » sont exclus du menu, tandis que les repas « Très fréquent » ont 90 % de chances d'être retenus avant le tirage des autres repas (dans la limite de 14 repas par semaine).
- Sur l'accueil et la page de génération, un utilisateur connecté voit un lien vers son profil (sa photo d'avatar) et un bouton de déconnexion. Un visiteur voit à la place le lien « Connexion ». La génération reste accessible sans connexion.
- La déconnexion envoie une requête `POST` avec jeton CSRF à `/deconnexion/`, puis redirige vers l'accueil (`/`).
- Les avatars disponibles sont des fichiers statiques dans `static/profile_pictures/` : `pfp_default.png` (avatar par défaut), `pfp_1.png` (Portrait 1) et `pfp_2.png` (Portrait 2). Le profil enregistre le nom du fichier choisi; l'application ne propose pas de téléversement d'image.
- Les comptes utilisent le modèle utilisateur standard de Django et sont stockés dans la base SQLite configurée par le projet. Exécuter `python manage.py migrate` avant le premier démarrage pour créer les tables nécessaires.

## Tests

```powershell
python manage.py test
```
