# Writeup - React Admin Route

## Objectif

Acceder a la page admin pour obtenir le flag.

## Analyse

1. L'app est une SPA React. La page d'accueil indique qu'une page admin existe.

2. Ouvrir les DevTools > Sources (ou Network). Le bundle principal est dans `assets/index-*.js`.

3. Rechercher dans le bundle : `"path"` ou `"Route"` ou une chaine ressemblant a `/xxxxx` (base64url).

4. Le chemin admin est injecte par Vite : `__ADMIN_PATH__` est remplace par une valeur comme `"/a1b2c3d4e5f6..."`.

5. Aller sur `http://<url>/<chemin_trouve>`. La page charge le flag via une API (le flag n'est jamais dans le bundle).

## Solution

```bash
# Exemple : trouver la route dans le bundle
curl -s http://localhost:8003 | grep -o 'assets/index-[^"]*\.js' | head -1
curl -s http://localhost:8003/assets/index-xxx.js | grep -oE '"/[A-Za-z0-9_-]+"' | sort -u
```
