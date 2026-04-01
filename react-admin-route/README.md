# React Admin Route

**Categorie:** Web  
**Difficulte:** Facile  
**Points:** 100  
**Flag:** `HIT{r34ct_r0ut3_0bfusc4t10n}`

---

## Description

> Une page admin protegee. Le chemin est aleatoire a chaque build.

**URL:** `http://<CHALLENGE_URL>:8003`

---

## Deploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8003

---

## Vulnérabilité

**Route obfusquee** — Le chemin de la page admin est genere aleatoirement au build (injecte via `define` dans Vite). Il est present en clair dans le bundle JavaScript. Le flag est servi par une API backend et n'apparait jamais dans le bundle. Analyser le fichier source (ex: `assets/index-*.js`) pour trouver la route `/xxxxx` et y acceder.
