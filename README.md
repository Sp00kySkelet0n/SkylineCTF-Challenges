# SkylineCTF - Guide de Contribution 🏰

![](Others/skylinectf.png)

Bienvenue dans le dépôt des challenges SkylineCTF ! Ce guide vous expliquera comment créer, sécuriser et publier votre challenge sur la plateforme.

---

## 🚀 Comment ajouter un challenge ?

Suivez ces 4 étapes simples pour voir votre challenge en ligne.

### 1. Préparation 🛠️
Clonez ce dépôt.
```bash
git clone https://github.com/Sp00kySkelet0n/SkylineCTF-Challenges.git
cd SkylineCTF-Challenges
```

### 2. Création du Challenge 📝
Créez un dossier pour votre challenge (par exemple `Mon-Challenge`).
Il doit contenir :
*   `Challenge.yaml` : La définition du challenge.
*   `Dockerfile` (si dockerisé).
*   `uploads/` (optionnel) : Fichiers associés au challenge à fournir aux joueurs.
*   `src/` (optionnel) : Code source (chiffré par le wizard).

> **💡 Astuce :** Vous pouvez utiliser le **Wizard** pour générer le `Challenge.yaml` automatiquement !
> Lancez `./wizard.sh` (ou `wizard.bat` sur Windows) et choisissez **📝 Créer un Challenge.yaml**.
> Le wizard vous posera les questions nécessaires (nom, description, catégorie, points, flag...) et générera le fichier pour vous.

---

## 📂 Structure du Challenge.yaml

Si vous préférez créer le `Challenge.yaml` manuellement, voici la structure à respecter :

### Type 1 : Challenge Docker (Web, Pwn...) 🐳
Utilise une image Docker et un port. Les points s'ajustent dynamiquement.

```yaml

apiVersion: skyline.local/v1 # Ne jamais modifier
kind: CTFChallenge # Ne jamais modifier
metadata:
  name: mon-challenge-unique # Doit correspondre au nom du dossier (lowercase, sans espaces)
  namespace: ctfd # Ne jamais modifier
spec:
  # Infos Générales
  name: "Titre du Challenge"
  description: "Trouvez le flag !"
  category: "Web"       # Web, Pwn, Crypto, Reverse...
  
  # Points Dynamiques (Recommandé)
  type: "dynamic"
  initial: 500          # Points de départ
  decay: 10             # Nombre de solutions pour baisse max
  minimum: 50           # Points minimum

  # Déploiement
  image: "ghcr.io/sp00kyskelet0n/skylinectf-challenges/chall:latest"
  port: 1337            # Port interne du conteneur
  instance: true        # Détermine si le challenge peut être déployé à la demande
  
  # Fichiers (si besoin de fournir un binaire/source)
  upload_files: true    # Upload tout le dossier 'uploads/' vers CTFd

  flag: "SKL{...}"    # À chiffrer avec le wizard !
```

### Type 2 : Challenge Statique (Forensic, Reverse) 📁
Pas de Docker, juste des fichiers à télécharger.

```yaml
apiVersion: skyline.local/v1
kind: CTFChallenge
metadata:
  name: mon-challenge-forensic # Doit correspondre au nom du dossier (lowercase, sans espaces)
  namespace: ctfd
spec:
  name: "Analyse Mystère"
  description: "Analysez ce fichier PCAP..."
  category: "Forensic"
  type: "standard"      # Ou dynamic
  points: 100
  
  upload_files: true    # Indispensable pour Forensic/Reverse !
  # Placez vos fichiers (PCAP, binaire...) (dans la limite de 50mb) dans le dossier 'uploads/' du challenge.
  
  flag: "SKL{...}"      # À chiffrer avec le wizard !
```

**Note sur la Connexion :** 
L'opérateur détecte automatiquement le protocole (`http://` ou `tcp://`) selon la catégorie et le port. Vous pouvez forcer via `connection_info: "..."`.

---

### 3. Sécurisation (Chiffrement) 🔐
**C'est l'étape la plus importante !** Protégez vos flags et votre code source avec notre assistant.

**Sur Linux / Mac :**
```bash
./wizard.sh
```

**Sur Windows :**
```cmd
wizard.bat
```

Le wizard vous propose deux options :

#### Option 1 : 📝 Créer un Challenge.yaml
Le wizard vous guide étape par étape pour générer le fichier :
1.  **Sélection du dossier** — Choisissez le dossier de votre challenge (il doit déjà exister).
2.  **Nom affiché** — Le titre visible sur CTFd (ex: `Mon Super Challenge`).
3.  **Description** — La description du challenge (multi-lignes, terminez par une ligne vide).
4.  **Catégorie** — Web, Pwn, Crypto, Forensic, Reverse, Misc...
5.  **Détection automatique du type** — Le wizard détecte si un `Dockerfile` et/ou un dossier `uploads/` existent pour configurer `instance` et `upload_files`.
6.  **Scoring** — Dynamique (initial/decay/minimum) ou statique (points fixes).
7.  **Port** — Le port interne du conteneur (uniquement si challenge dockerisé).
8.  **Flag** — Le flag du challenge (ex: `SKL{...}`).
9.  **Créateur** — Votre nom/pseudo.

> Le `metadata.name` et l'`image` Docker sont déduits automatiquement du nom de dossier.

À la fin, le wizard propose d'enchaîner directement avec le chiffrement et la soumission.

#### Option 2 : 🔐 Sécuriser un challenge existant
Pour un challenge dont le `Challenge.yaml` existe déjà :
1.  **Chiffrement du `Challenge.yaml`** — Les champs sensibles (flag, etc.) sont chiffrés avec SOPS.
2.  **Chiffrement du `WALKTHROUGH.md`** — Le writeup est chiffré avec GPG (si présent).
3.  **Chiffrement du `src/`** — Le code source est zippé et chiffré avec GPG (optionnel).
4.  **Soumission via Pull Request** — Fork automatique, upload des fichiers, et création de la PR.

**C'est tout !** Vos fichiers sont prêts et soumis.

### 4. Publication ✈️
Une fois vos fichiers sécurisés :

1.  Ajoutez vos fichiers (les versions chiffrées !) :
    ```bash
    git add Mon-Challenge/Challenge.yaml
    git add Mon-Challenge/src.zip.gpg
    git add Mon-Challenge/Dockerfile
    ```
2.  Commitez et Pushez :
    ```bash
    git commit -m "feat: Ajout du challenge Mon-Super-Challenge"
    git push origin ma-branche
    ```
3.  Ouvrez une Pull Request. Une fois validée, Flux déploiera automatiquement votre challenge sur le cluster ! 🚀

> **💡 Astuce :** Le wizard peut aussi soumettre automatiquement via Pull Request à la fin du processus de sécurisation !

---

## ℹ️ Fonctionnement Technique

### Infrastructure as Code (IoC)
SkylineCTF utilise une approche GitOps. Tout ce qui est sur la branche `main` est la vérité absolue du cluster.

### Déploiement Automatique
1.  **Flux** détecte les modifications.
2.  **SkylineOperator** lit votre `Challenge.yaml`.
3.  Le challenge est créé dans **CTFd** et déployé sur le cluster Kubernetes.

### Architecture
![](Others/challenge_creation_process.png)

*Pour les instances à la demande (Pods/VMs) :*
![](Others/instance_deployment_diagram.png)
