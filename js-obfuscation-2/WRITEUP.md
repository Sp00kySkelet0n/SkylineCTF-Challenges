# Writeup - JS Obfuscation 2

## Pourquoi coller dans la console ne marche pas

Le script utilise `document.currentScript` pour acceder a son propre code source. Quand on colle du code dans la console, il n'est pas associe a un element `<script>` : `document.currentScript` vaut `null`, et le script sort immediatement via `if(!_0x3c4d){return;}`.

## Resolution

### Etape 1 : Inspecter le code source

View Source (Ctrl+U) ou Elements > chercher le script. On trouve un commentaire :

```javascript
/*Z:{{ payload }}*/
```

Le payload est une chaine base64 injectee par le serveur.

### Etape 2 : Deobfusquer la logique

Les chaines hex (`\x6c\x65\x6e\x67\x74\x68` = "length", etc.) peuvent etre decodees avec un outil ou manuellement. La logique :

1. Extraire le contenu du commentaire avec la regex `/\*Z:([^*]+)\*/`
2. `atob()` pour decoder le base64
3. XOR chaque octet avec la cle `0x59^0x03` = `0x5A` = 90

### Etape 3 : Decoder manuellement

En Python :

```python
import base64
payload = "..."  # copier depuis le commentaire /*Z:...*/
decoded = base64.b64decode(payload)
flag = bytes(b ^ 0x5A for b in decoded).decode()
print(flag)
```

Ou en JS (sur la page, avec le payload copie) :

```javascript
const payload = "...";  // depuis /*Z:...*/
const decoded = atob(payload);
const flag = [...decoded].map(c => String.fromCharCode(c.charCodeAt(0) ^ 0x5A)).join('');
console.log(flag);
```

### Etape 4 : Alternative - executer dans le contexte de la page

On peut aussi recuperer le script via `document.scripts`, extraire son `textContent`, parser le commentaire et decoder. Mais extraire le payload du source et le decoder manuellement reste la methode la plus directe.

## Flag

`HIT{0bfusc4t10n_v2_h4rd3r}`
