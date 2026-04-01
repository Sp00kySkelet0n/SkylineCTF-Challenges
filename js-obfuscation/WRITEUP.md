# Writeup - JS Obfuscation

## Methode 1 : Execution dans la console

1. Ouvrir la page du challenge
2. F12 pour ouvrir les DevTools, onglet Console
3. Copier le contenu du IIFE (la fonction anonyme dans le script)
4. L'executer : le IIFE retourne le flag directement

```javascript
(function(){
    var _0x4a2f=['\x48\x49\x54\x7b','\x30\x62\x66\x75\x73\x63\x34\x74\x31\x30\x6e\x5f\x31\x73\x5f\x33\x7a\x7d'];
    var _0x5e9d=function(_0x3f){return _0x3f['split']('')['map'](function(_0xa){return _0xa['charCodeAt'](0);})['reduce'](function(_0xa,_0xb){return _0xa+String['fromCharCode'](_0xb);},'');};
    var _0x7c1b=_0x4a2f['map'](_0x5e9d)['join']('');
    return _0x7c1b;
})();
```

Ou plus simple : modifier le script pour afficher le resultat :

```javascript
console.log((function(){...})());
```

## Methode 2 : Decodage manuel des sequences hex

Les chaines `\xNN` sont des caracteres en notation hexadecimale :
- `\x48` = H, `\x49` = I, `\x54` = T, `\x7b` = {
- `\x30` = 0, `\x62` = b, `\x66` = f, etc.

Decoder chaque sequence donne : `HIT{0bfusc4t10n_1s_3z}`

## Methode 3 : Outils de deobfuscation

- [de4js](https://lelinhtinh.github.io/de4js/) : colle le script, decode
- [JSNice](http://jsnice.org/) : reformate et renomme les variables

## Flag

`HIT{0bfusc4t10n_1s_3z}`
