# Write-Up - Paradox Machine (SSTI → RCE)

## Reconnaissance

On accède à `http://localhost:8003` et on tombe sur une page de login pour la "Paradox Machine". On se connecte avec le compte fourni :
- **Username:** `operator`
- **Password:** `operator`

On arrive sur un simulateur temporel avec deux champs :
- **Temporal Coordinates** (obligatoire)
- **Simulation Parameters** (optionnel)

### Indices

En vérifiant `/robots.txt` :
```
User-agent: *
Disallow: /simulator
Disallow: /flag.txt
```

On sait maintenant :
- Le flag est dans **`/flag.txt`**
- Le simulateur est accessible à travers **`/simulator`**

---

## Confirmer la SSTI

On entre dans le champ "Temporal Coordinates" :

```
{{7*7}}
```

Le résultat affiche **49** au lieu de `{{7*7}}` → **SSTI confirmée !**

---

## Flag

```
HIT{sst1_p4r4d0x_rce_t1m3l1n3_br34ch}
```

---

## Remédiation

### 1. Utiliser `SandboxedEnvironment`
```python
# Vulnérable
from jinja2 import Environment, BaseLoader
env = Environment(loader=BaseLoader())

# Sécurisé
from jinja2.sandbox import SandboxedEnvironment
env = SandboxedEnvironment()
```

### 2. Ne jamais injecter l'input utilisateur dans le template
```python
# Vulnérable — input dans le template string
template_str = f"<p>{user_input}</p>"
env.from_string(template_str).render()

# Sécurisé — input passé comme variable
template_str = "<p>{{ coordinates }}</p>"
env.from_string(template_str).render(coordinates=user_input)
```

### 3. Filtrer/Escape les entrées
```python
from markupsafe import escape
safe_input = escape(user_input)
```

### 4. Principe du moindre privilège
- Exécuter l'app avec un utilisateur non-root
- Limiter les permissions fichier dans le container
- Ne pas stocker le flag dans un fichier accessible

---

## Références

- [HackTricks — SSTI Jinja2](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection/jinja2-ssti)
- [PayloadsAllTheThings — SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
- [CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine](https://cwe.mitre.org/data/definitions/1336.html)
- [PortSwigger SSTI Labs](https://portswigger.net/web-security/server-side-template-injection)
