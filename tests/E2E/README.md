# E2E - Point d'entree unique

Ce document est le point d'entree unique pour le contexte et le scenario E2E.

## Scripts E2E (ce dossier)

- `run_e2e_process.py`: orchestration complete du scenario (fixtures serveur, sync, scans, soft/hard delete, verifs).
- `seed_local_e2e_data.py`: seed local ciblé pour la DB timbreuse2022.
- `test_handle_deleted_remote_badge_mock.py`: test unitaire rapide/stable (sans Docker ni DB).
- `test_integration_legacy_remote_delete.py`: test d'integration legacy (Docker + DB/API), plus sensible a l'environnement.
- `logs/`: sorties de tests E2E (`E2E_logs.txt`).

## Contexte fusionne

Ce workspace contient deux projets distincts mais complementaires :

- `..\Timbreuse\`
- `..\timbreuse-srv\`

### Projet Timbreuse (client)

Application Python de pointage RFID pour l'entreprise.

Composants principaux :
- interface tactile (Pygame),
- base locale MariaDB,
- lecteur RFID,
- synchronisation avec l'API serveur.

But fonctionnel :
- enregistrer les entrees/sorties des utilisateurs,
- calculer automatiquement les heures de travail.

### Projet timbreuse-srv (serveur)

Backend web CodeIgniter 4 (PHP) + MariaDB.

Role principal :
- gerer les utilisateurs et leurs droits,
- piloter la logique metier de pointage (badge, logs, synchronisation),
- exposer les routes API/admin consommees par l'application client,
- centraliser le modele de donnees.

`timbreuse-srv` est la source de verite cote serveur.

### Objectif

Mettre en place un test d'integration de bout en bout reliant les deux projets dans un environnement de test unique.

Objectifs de validation :
- simuler une activite de timbreuse (scan badge + interactions),
- verifier la synchronisation des donnees vers `timbreuse-srv`,
- supprimer l'utilisateur cote serveur,
- scanner a nouveau le badge et valider le comportement client.

### Comportement attendu apres suppression distante

Lors du scan suivant, l'application cliente doit utiliser la logique de `handle_deleted_remote_badge()` dans `main.py` :

- si la correspondance distante n'existe plus mais existe localement :
  - suppression de la correspondance locale,
  - message indiquant que le badge n'est plus attribue a l'utilisateur,
  - message confirmant la suppression locale.
- si la correspondance n'existe ni a distance ni localement :
  - message "Ce badge n'est pas attribue a un utilisateur."

Puis l'application attend l'acquittement du modal via `wait_modal_ack()`.

## Synopsis / Genese (fusion de Bug_fixing.md)

### Probleme observe

Quand un element est supprime definitivement cote serveur (ex: user ou badge), la suppression n'etait pas toujours repercutee cote timbreuse locale.

### Pourquoi le bug arrivait

- La sync historique etait principalement basee sur des snapshots incrementaux (`date_modif >= startDate`).
- Ce mode couvre bien create/update et les soft deletes (ligne encore presente avec `date_delete`).
- En hard delete, la ligne n'existe plus dans la table source -> aucun "signal de suppression" n'est transmis.
- Le client conserve donc une correspondance locale obsolete faute d'evenement explicite.

### Direction de correction

- Passer d'une logique "snapshot/upsert" a une logique "journal d'evenements" pour les suppressions.
- Cote serveur: ecrire des events de type suppression (ici `hard_delete`) et les exposer via API.
- Cote client: importer ces events, les appliquer localement de facon idempotente, puis marquer `processed=1`.

### Resultat cible valide par ce dossier E2E

- Generation d'evenements de suppression cote `timbreuse-srv`.
- Transmission vers Timbreuse.
- Application locale des suppressions.
- Verification fonctionnelle via scans et verification technique via `event_log_sync.processed=1`.

## Processus E2E fusionne

### 1. Implementation dans ci4 de timbreuse-srv

**Date 30 mars 2026**

- Ajout des badges (3 badges) numero de badge factice a generer
  - Badge 1 utilise jusqu'au 3 avril 2026 pour les 8 premiers logs du user 1
  - Badge 2 non attribue pour le moment
  - Badge 3 utilise pour le user 2
- Creation des users associes (3 users)
  - User 1 : associe au badge 1
  - User 2 : associe au badge 3 jusqu'au 31 mars
  - User 3 : absent de la DB au debut
- Creation des logs
  - 8 pour User 1 (badge 1)
  - 6 pour User 2 (badge 3)
  - aucun pour User 3

### 2. Phase de test pre-suppression sur la Timbreuse

Chaque processus affiche des donnees et des codes de succes/erreur. Les donnees sont stockees dans `tests/E2E/logs/E2E_logs.txt`.

**Date 1er avril 2026**

- Scan badge 1 -> affichage des logs du user 1
- Scan badge 2 -> message badge non attribue
- Scan badge 3 -> affichage uniquement des logs du user 2

### 3. Action de suppression de donnees dans timbreuse-srv

Regles/contraintes :

- Le badge 1 doit etre supprime dans l'intervalle de non-utilisation des badges 1 et 2
- Le user 2 doit etre supprime de la DB
- Deux cycles:
  - cycle soft delete
  - cycle hard delete

### 4. Phase de test post-suppression

#### 4.1 L'entre 2 cas (actions 4/5 avril)

- Badges :
  - Badge 1 : suppression complete DB -> hard delete -> envoi event_log vers timbreuse
  - Badge 2 : attribue a user 1
  - Badge 3 : attribue a user 3
- Users :
  - soft delete du user 2
- Logs :
  - ajout de 2 logs user 1 (badge 2, 6 avril)
  - ajout de 4 logs user 3 (badge 3, 6 avril)

#### 4.2 Cas soft delete (date 3 avril)

- Scan badge 1 -> erreur "badge plus attribue", logs user 1 visibles
- Scan badge 2 -> erreur "badge non attribue"
- Scan badge 3 -> erreur "badge plus attribue", logs user 2 non visibles

#### 4.3 Cas hard delete (date 6 avril)

- Scan badge 1 -> erreur "badge plus attribue", logs user 1 visibles
- Scan badge 2 -> affichage de l'ensemble des logs user 1
- Scan badge 3 -> affichage de l'ensemble des logs user 3

#### 4.4 Clarification sequence 5 etapes

- Etape 1 : hard delete de `badge 1` uniquement
- Etape 2 : soft delete de `user 2` et reattribution de `badge 3` a `user 3`
- Etape 3 : scan `badge 3` -> seuls les logs de `user 3` apparaissent
- Etape 4 : hard delete de `user 2`
- Etape 5 : nouveau scan `badge 3` -> seuls les logs de `user 3` apparaissent

#### 4.5 Clarification verification technique obligatoire

- verifier qu'un event `hard_delete` est cree dans `event_type` cote serveur
- verifier que l'event est recu cote timbreuse dans `event_log_sync`
- verifier que l'event est traite puis passe a `processed=1`

## Journal E2E

Le journal principal est ecrit dans:

- `tests/E2E/logs/E2E_logs.txt`

## Contenu fusionne depuis Correctif_E2E.md

### A. Points clarifies (reproductibilite)

- IDs fixes badges: `900000000001`, `900000000002`, `900000000003`.
- Naming convention comptes web: `e2e_<scenario>_u<1|2|3>` (minuscules/chiffres/_).
- Soft delete: ligne conservee avec `date_delete` non NULL.
- Hard delete: suppression physique ciblee (`badge_sync`, `user_sync`) selon le scenario.
- Contrat event logs attendu par Timbreuse:
  - `id_event`, `event_type`, `entity_type`, `entity_id`, `payload`, `date_event`.
- Verification technique obligatoire:
  - import event dans `event_log_sync`,
  - traitement local puis `processed=1`.

### B. Procedure pratique (copier-coller)

Pre-requis obligatoire avant toute execution E2E:

- L'environnement `timbreuse-srv` doit etre installe de bout en bout et pleinement operationnel (containers Docker demarres, DB accessible, migrations appliquees, utilisateur de test cree).
- Sans cette mise en place complete, le scenario E2E ne peut pas etre execute de facon fiable.

```powershell
cd ..\timbreuse-srv
docker compose up -d
docker exec -i timbreuse-srv-mariadb-1 mariadb -uroot -proot -e "DROP DATABASE IF EXISTS ci4; CREATE DATABASE ci4 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
docker exec -i timbreuse-srv-apache-1 php spark migrate --all
docker exec -i timbreuse-srv-apache-1 php tests/tools/create_test_timbreuse_user.php
```

Puis lancer le scenario:

```powershell
cd ..\Timbreuse
$env:TIMBREUSE_API_BASE_URL="http://localhost"
$env:TIMBREUSE_API_KEY_FILE=".key.json"
.\.venv\Scripts\python.exe tests/E2E/run_e2e_process.py
```

Modes d'execution assertions SQL:

```powershell
# Mode strict (defaut): stop au 1er FAIL
.\.venv\Scripts\python.exe tests/E2E/run_e2e_process.py --strict

# Mode non-strict: continue, puis FAIL global en fin d'execution s'il y a des erreurs
.\.venv\Scripts\python.exe tests/E2E/run_e2e_process.py --non-strict
```

Par defaut, `run_e2e_process.py` applique automatiquement un profil local Docker:

- `TIMBREUSE_API_BASE_URL=http://localhost`
- `TIMBREUSE_API_KEY_FILE=.key.json`
- `E2E_SERVER_DB=ci4`
- `E2E_SERVER_DB_USER=root`
- `E2E_SERVER_DB_PASSWORD=root`
- `E2E_SERVER_DB_HOST=127.0.0.1`
- `E2E_SERVER_DB_PORT=3307`

Tu peux toujours surcharger ces valeurs via des variables d'environnement avant l'execution si besoin.

Tests cibles:

```powershell
# Test unitaire (rapide)
.\.venv\Scripts\python.exe tests/E2E/test_handle_deleted_remote_badge_mock.py

# Test integration legacy (environnement Docker requis)
.\.venv\Scripts\python.exe tests/E2E/test_integration_legacy_remote_delete.py --username test_timbreuse
```

### C. Critere PASS minimal

- Le scenario va jusqu'a la fin sans exception.
- Les scans attendus correspondent au processus defini dans ce README.
- Les hard delete generent des events et le traitement local positionne `processed=1`.

## Validation objective SQL (recommandee)

Le script `run_e2e_process.py` ecrit maintenant des snapshots SQL serveur/local dans:

- `tests/E2E/logs/E2E_logs.txt`

Format:

- `Snapshot DB [<etape>] | {...json...}`

Etapes journalisees:

- `apres_fixture_et_sync_initiale`
- `apres_etape1_hard_delete_badge1`
- `apres_etape2_soft_delete_user2_reattrib_badge3`
- `apres_etape4_hard_delete_user2`

Champs verifies (serveur + local):

- existence/suppression badge 1
- attribution du badge 3
- presence/soft delete user 2
- events `hard_delete` (serveur `event_type`)
- reception + traitement `processed=1` (local `event_log_sync`)

Cette trace permet de valider les etapes E2E avec des faits SQL, en plus du comportement fonctionnel au scan.

## Assertions PASS/FAIL et CI

`run_e2e_process.py` journalise maintenant des lignes explicites:

- `PASS [<etape>] ...`
- `FAIL [<etape>] ...`
- `E2E PASS - toutes les assertions sont valides.`
- `E2E FAIL - ...`

Comportement:

- en `--strict` (defaut): arret immediat au premier `FAIL`
- en `--non-strict`: le script poursuit toutes les etapes, puis renvoie un `FAIL` global en fin de scenario s'il y a au moins une assertion en echec

Impact CI:

- code retour `0` si toutes les assertions passent
- code retour non-zero si au moins une assertion echoue ou si une exception survient

## Note architecture

Les mecanismes de resilience specifiques E2E (ex: retry sur `Lock wait timeout`) sont scopes au script `run_e2e_process.py` via une classe dediee (`E2EModel`), afin de ne pas imposer de comportement de test au runtime applicatif standard.
