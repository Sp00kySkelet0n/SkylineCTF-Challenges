# JS Obfuscation

**Categorie:** Reverse / Obfuscation  
**Difficulte:** Facile  
**Points:** 100  
**Flag:** `HIT{0bfusc4t10n_1s_3z}`

---

## Description

> Un script JavaScript obfusque protege un secret. Trouve-le.

**URL:** `http://<CHALLENGE_URL>:8003`

---

## Deploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8003

---

## Vulnérabilite

**Obfuscation JavaScript** — Le flag est encode dans le script via des sequences hexadecimales (`\xNN`) et des noms de variables obfusques. Le participant doit soit :
- Executer le script dans la console du navigateur (le IIFE retourne le flag)
- Deobfusquer manuellement les chaines hex
- Utiliser un outil de deobfuscation (de4js, jsnice, etc.)
