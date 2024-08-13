# rfid pyton raspberry pi
- [mfrc522 PyPI](https://pypi.org/project/mfrc522/#description)
- [mariadb PyPI](https://pypi.org/project/mariadb/)
- [pygame](https://pypi.org/project/pygame/)
- [pygame-vkeyboard](https://pypi.org/project/pygame-vkeyboard/)

```bash
apt install mariadb-server
```

## À ajouter ?
- [x] voir le nom attribué à l’id
- [x] sur l’écran d’attente voir les derniers pointages
- avoir une scène de confirmation récapitulatif
- couleur de orif 
    - #005BA9 bannière, titre
    - #DBCEB1 fond
    - #AE9B70 text
    - #FFFFFF
    https://coolors.co/005ba9-dd1c1a-dbceb1-386641-3c362a
- [x] wait screen avec rebond du text avec les bords
- [x] 5 dernières décroisant
- [x] nom, prénom
- [x] temps limite
- horaire d'allumage du Raspberry Pi
- écran de confirmation du nom d'utilisateur entrer lors de la création




## sécurité
- [ ] stockage temporaire des noms
- [ ] hacher (sha2) les ids des badges
- [ ] chiffrement de la connexion avec la base de données

## à corrigé
- [x] scene with unknow badge
- [x] request log with unknow badge
- [x] somme heures plus 24 heures
- [x] désactiver la mise en veille de l'écran
- [ ] les câbles ?
- [ ] requête log quand le bouton est appuyé
- [ ] ferme proprement le script quand la view est fermé
- [x] mettre le jeton d’identification aussi pour le get log de l’api 

## bug
- [ ] plus de 12 logs dans le détail d'un provoque un empilement des caractère
- [ ] Utilisateur peut mettre un nom vide
- [ ] Utilisateur peut mettre un nom à double
- [x] Un badge avec un user id à NULL provoque un dysfonctionnement de la 
synchronisation

## À faire
* [ ] changer log_sync
* [ ] changer les procedure strocked utilisant log_sync
* [ ] changer la fonction python qui appelle la processure strocked utilisant log_sync

## À faire plus tard
* [x] mettre à jour la view log
* [ ] rajouter l’affichage des date de modification


## À voir
- [ ] voir pour remettre les contraintes de clé étrangère sur les tables _write
- [ ] enlever peut-être la contraint de clé étrangère sur les table sync sur la
 timbreuse

## truc à tester avec de mettre sur la production
- [x] envoye log + pas de fuite de connection/mémoire avec SHOW PROCESSLIST;
- [s] envoye badge user + fuite
- [s] table write vide
- [s] création db à zéro
- [s] modification nom user
- [s] modificatio log 
- [s] suppretion log
- [s] téléchargement log site
- [s] temps cours si pas de connection
- [s] sauvegarder la db du serveur distant
- [x] mettre vrai url avant commit
- [ ] commit
- [ ] pull
- [ ] mettre l’autorisation sur run.sh
- [ ] mettre faux url sur version local du pc de bureau
