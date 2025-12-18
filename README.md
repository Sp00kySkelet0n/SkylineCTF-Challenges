# SkylineCTF
![](skylinectf.png)

## Processus de création d'un challenge

SkylineCTF propose ses propres objets Kubernetes pour définir un challenge.

Ces objets dès qu'ils seront déployés dans le cluster seront créés dans le CTFd via le SkylineOperator.

Il est possible d'appliquer manuellement un challenge via kubectl mais la manière recommandée est de pousser le challenge sur le dépôt "https://github.com/Sp00kySkelet0n/SkylineCTF-Challenges".

Une fois poussés sur le dépôt et validés par un administrateur via la branche master Flux va synchroniser ces objets et les déployer automatiquement dans le cluster.

![](Images/challenge_creation_process.png)

## Processus de création d'instance 

SkylineCTF propose ses propres objets Kubernetes pour définir une instance unique et temporaire d'un challenge par équipe.

Ces objets Kubernetes seront déployés dans le cluster par la plateforme SkylineDeployer et seront déployés via un pod ou une VM windows en fonction du type de challenge par le SkylineOperator.

![](Images/instance_deployment_diagram.png)


