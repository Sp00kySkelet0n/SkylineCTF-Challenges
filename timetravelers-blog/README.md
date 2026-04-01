# Challenge 01 - TimeTraveler's Blog

**Catégorie:** Web  
**Difficulté:** Facile  
**Points:** 100  
**Flag:** `HIT{x55_t1m3_tr4v3l_1s_d4ng3r0us}`

---

## Description (à afficher aux participants)

> **Titre:** TimeTraveler's Blog.
>
> **Description:** Bienvenue dans le blog des voyageurs temporels !
>
> Le Dr. Chronos tient un blog où les chronautes partagent leurs aventures à travers le temps. Un système de commentaires permet à chacun d'envoyer ses « transmissions temporelles ».
>
> **L'admin du blog vérifie régulièrement les commentaires.** On dit qu'il transporte un secret important dans ses cookies...
>
> **URL:** `http://<CHALLENGE_URL>:8000`

---

## Déploiement

```bash
docker compose up --build -d
```

L'app sera accessible sur :

- **Blog :** http://localhost:8000
- **Admin Bot API :** http://localhost:3000 (POST `/visit` avec `url=...`)

---

## Stack technique

- FastAPI + Jinja2 (autoescape désactivé)
- SQLite
- Playwright (headless Chromium) pour le bot admin
- Docker

---

## Vulnérabilité

**Stored Cross-Site Scripting (XSS)** — CWE-79

Le template Jinja2 a l'autoescaping désactivé (`templates.env.autoescape = False`). Les commentaires sont stockés en base tels quels et rendus sans échappement dans le HTML :

```html
<!-- post.html -->
<div class="comment-content">
  {{ comment.content }}
  <!-- Pas d'échappement ! -->
</div>
```

Un attaquant peut injecter du JavaScript dans un commentaire. Quand le bot admin visite la page, le script s'exécute dans son navigateur et peut exfiltrer ses cookies (dont le flag).
