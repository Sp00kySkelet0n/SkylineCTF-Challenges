# Challenge 04 - Paradox Machine

**Catégorie:** Web  
**Difficulté:** Difficile  
**Points:** 500  
**Flag:** `HIT{sst1_p4r4d0x_rce_t1m3l1n3_br34ch}`

---

## Description (à afficher aux participants)

> **Titre:** Paradox Machine.
>
> **Description:** La Paradox Machine est le simulateur temporel le plus puissant jamais construit. Les opérateurs y entrent des coordonnées spatio-temporelles pour simuler les paradoxes potentiels avant chaque saut.
>
> Un compte opérateur de test est disponible :
>
> - **Username:** `operator`
> - **Password:** `operator`
>
> Le moteur de simulation semble traiter vos entrées d'une manière particulière... Certains disent que la machine est plus puissante qu'on ne le pense. Un fichier confidentiel contenant des coordonnées critiques serait stocké quelque part sur le serveur.
>
> **URL:** `http://<CHALLENGE_URL>:8003`

---

## Déploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8003

---

## Stack technique

- FastAPI + Jinja2 (Environment sans sandboxing)
- SQLite
- Docker

---

## Vulnérabilité

### Server-Side Template Injection (SSTI) — CWE-1336

L'input utilisateur dans le champ "Temporal Coordinates" est injecté directement dans un template Jinja2 via string formatting, puis rendu avec `env.from_string()` :

```python
template_str = f"""
    ...
    <span class="field-value">{coordinates}</span>
    ...
"""
rendered = env.from_string(template_str).render()
```

L'`Environment` Jinja2 est instancié sans sandboxing (`SandboxedEnvironment`), permettant l'accès à l'arbre de classes Python et l'exécution de code arbitraire.

### Information Disclosure additionnelle

- `/robots.txt` contient des commentaires mentionnant Jinja2, le manque de sandboxing, et l'emplacement du flag (`/flag.txt`)
