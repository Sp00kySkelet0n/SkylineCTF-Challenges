# Cookie Admin

**Categorie:** Web  
**Difficulte:** Trivial  
**Points:** 50  
**Flag:** `HIT{c00k13_r0l3_4dm1n_1s_3z}`

---

## Description

> Une page admin protegee. Trouve comment y acceder.

**URL:** `http://<CHALLENGE_URL>:8002`

---

## Deploiement

```bash
docker compose up --build -d
```

Accessible sur : http://localhost:8002

---

## Vulnérabilité

**Cookie non verifie** — L'app verifie uniquement la presence du cookie `role=admin`. Il suffit de le definir dans le navigateur (DevTools > Application > Cookies) ou via une extension pour acceder a /admin et obtenir le flag.
