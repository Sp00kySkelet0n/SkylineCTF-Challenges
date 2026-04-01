# JS Obfuscation 2

**Categorie:** Reverse / Obfuscation  
**Difficulte:** Moyen  
**Points:** 200  
**Flag:** `HIT{0bfusc4t10n_v2_h4rd3r}`

---

## Description

> Le coffre-fort a ete renforce. La cle est toujours cachee.

**URL:** `http://<CHALLENGE_URL>:8004`

---

## Deploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8004

---

## Vulnérabilite

**Obfuscation multi-couches** — Le flag est encode en base64 puis XOR avec une cle. Le payload est dans un commentaire du script. Le script utilise `document.currentScript` pour lire son propre contenu : coller le code dans la console echoue (currentScript est null). Le participant doit deobfusquer pour comprendre l'algorithme (atob + XOR) et extraire manuellement le flag depuis le commentaire `/*Z:...*/`.
