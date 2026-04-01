# Writeup - JS Obfuscation 3

## Misdirection

La page d'accueil est un leurre. Le payload decode donne l'indice vers la vraie epreuve.

## Etape 1 : Decoder le faux challenge

Le payload utilise :
1. **Alphabet base64 personnalise** : `s3HXunU82JdSpkQWzqeTfLZox/hY4E6VyKA9cta1Mjwmg7N0BCblFi5rG+I=PRvDO` (correspondance 1:1 avec l'alphabet standard)
2. **XOR position-dependant** : chaque octet XOR avec `(0x3F + position) % 256`

Algorithme (extrait du script) :
- Traduire custom -> standard (indexOf dans _0x1, charAt dans _0x2)
- atob() pour decoder le base64
- XOR chaque octet avec (0x3F + i) % 256

En JavaScript :

```javascript
const CUSTOM = 's3HXunU82JdSpkQWzqeTfLZox/hY4E6VyKA9cta1Mjwmg7N0BCblFi5rG+I=PRvDO';
const STANDARD = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
const payload = '...';  // depuis la page
const decoded_b64 = [...payload].map(c => STANDARD[CUSTOM.indexOf(c)]).join('');
const raw = atob(decoded_b64);
const msg = [...raw].map((b, i) => String.fromCharCode(b.charCodeAt(0) ^ ((0x3F + i) % 256))).join('');
console.log(msg);  // 0x7a2f
```

## Etape 2 : Trouver la vraie page

Le message decode donne `0x7a2f` (notation hex). A interpreter comme chemin : `/0x7a2f`

## Etape 3 : Resoudre la vraie epreuve

Sur http://.../0x7a2f : 20 redirections successives (0x7a2f -> 0x7a2f/1 -> ... -> 0x7a2f/20). La derniere page affiche un faux 404. Le flag est dans un commentaire HTML du code source : `<!-- FLAG: HIT{...} -->`

## Flag

`HIT{0bfusc4t10n_v3_tr0ll3d}`
