# JS Obfuscation 3

**Categorie:** Reverse / Obfuscation  
**Difficulte:** Difficile  
**Points:** 300  
**Flag:** `HIT{0bfusc4t10n_v3_tr0ll3d}`

---

## Description

> Le coffre-fort ultime. Decode le message pour obtenir la cle.

**URL:** `http://<CHALLENGE_URL>:8005`

---

## Deploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8005

---

## Vulnérabilite

**Misdirection** — La page d'accueil affiche un payload encode avec un alphabet base64 personnalise + XOR position-dependant. Une fois decode : "0x7a2f". Le participant doit interpreter 0x7a2f comme le chemin /0x7a2f. 20 redirections mènent a une fausse page 404 ou le flag est en commentaire dans le HTML.
