# Challenge 02 - Chronobank

**Catégorie:** Web  
**Difficulté:** Moyen  
**Points:** 200  
**Flag:** `HIT{1d0r_4nd_sql1_t1m3_h31st}`

---

## Description (à afficher aux participants)

> **Titre:** Chronobank.
>
> **Description:** Le système bancaire temporel le plus sécurisé de 2147.
>
> *Bienvenue à la Chronobank, le système bancaire temporel le plus sécurisé de 2147.*
>
> Un compte de test vous a été fourni :
> - **Username:** `traveler42`
> - **Password:** `backto1985`
>
> Mais le véritable objectif est d'accéder au coffre-fort (Vault) de l'administrateur, le **Dr. Chronos**. On murmure qu'il y garde des codes d'accès temporels hautement confidentiels...
>
> **URL:** `http://<CHALLENGE_URL>:8001`
---

## Déploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8001

---

## Stack technique

- FastAPI + Jinja2
- SQLite (queries vulnérables)
- Sessions en mémoire (dict Python)
- Docker

---

## Vulnérabilités

### 1. SQL Injection — Authentication Bypass (CWE-89)

Le endpoint `/login` utilise la concaténation de strings pour construire la requête SQL :

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed}'"
```

Un attaquant peut injecter du SQL dans le champ `username` pour bypasser l'authentification.

### 2. IDOR — Insecure Direct Object Reference (CWE-639)

Le endpoint `/api/vault/{user_id}` ne vérifie pas que le `user_id` demandé correspond à l'utilisateur connecté. N'importe quel utilisateur authentifié peut accéder au vault de n'importe quel autre utilisateur.

Le endpoint `/account/{account_id}` souffre du même problème.
