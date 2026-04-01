# Challenge 03 - Temporal API

**Catégorie:** Web / API  
**Difficulté:** Moyen+  
**Points:** 300  
**Flag:** `HIT{jwt_n0n3_4lg0_t1m3_tr4v3l_cl34r4nc3}`

---

## Description (à afficher aux participants)
> **Titre:** A propos du temps.
>
> **Description:** Le Temporal Research Institute dispose d'une API REST interne pour gérer ses missions de voyage temporel.
>
> Un compte "invité" est disponible :
> - **Username:** `guest`
> - **Password:** `guest`
>
> Mais les informations les plus sensibles sont réservées aux administrateurs de **Temporal Command**. L'Omega Protocol, classifié au plus haut niveau, contiendrait des coordonnées temporelles d'une importance capitale...
>
> L'API semble utiliser des JWT pour l'authentification. Peut-être que leur implémentation cache des faiblesses ?
>
> **URL:** `http://<CHALLENGE_URL>:8002`

---

## Déploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8002

---

## Stack technique

- FastAPI (API REST, Swagger UI activé)
- PyJWT 2.8.0
- SQLite
- Docker

---

## Vulnérabilités

### 1. JWT signé avec un secret faible (CWE-521)
Le secret utilisé est `"time"` — crackable en secondes avec hashcat ou jwt_tool.

### 2. Algorithm "none" accepté (CWE-345)
Le serveur décode les JWT avec `algorithms=["HS256", "none"]`, acceptant les tokens non signés.

### 3. Broken Access Control via JWT claims (CWE-285)
Le rôle (`role`) et le niveau de clearance (`clearance`) dans le JWT contrôlent l'accès aux ressources. En forgeant un token avec `role: "admin"` et `clearance: 5`, on accède à tout.

### 4. Information Disclosure (CWE-200)
- Swagger UI activé (`/docs`)
- Endpoint `/api/v1/debug/health` leak le type d'algorithme
- Endpoint `/api/v1/debug/token-info` décode les tokens sans vérification
