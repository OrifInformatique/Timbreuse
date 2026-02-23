# Architecture technique — Timbreuse

## Vue d'ensemble

L'application suit un pattern **MVC multi-threadé** :

```mermaid
graph LR
    main["main.py<br/>(Controller)"]
    view["view.py<br/>(View / Pygame)"]
    model["model.py<br/>(Model / MariaDB)"]
    api["api_client.py<br/>(API sync)"]
    rfid["rfid.py / fake_rfid.py<br/>(Input)"]

    main -->|thread| view
    main --> model
    main --> rfid
    view --> model
    model --> api
```

## Flux principal

```mermaid
flowchart TD
    A[App.load] --> B[Démarrer view.load dans un thread]
    A --> C[Synchronisation serveur distant]
    A --> D[Boucle App.update]

    D --> E[Sync avant RFID]
    E --> F[do_rfid — attend un badge]
    F --> G[Sync après RFID]
    G --> H[do_model_request — cherche utilisateur en DB]
    H --> I{Badge connu ?}
    I -->|Oui| J[Écran Entrée / Sortie]
    I -->|Non| K[Écran clavier — saisie nom]
    J --> L[wait_choice — attend le clic]
    K --> L
    L --> M[invoke_insert — enregistre le log]
    M --> N[reset — retour attente]
    N --> D
```

## Communication inter-threads

`main.py` et `view.py` communiquent via un dictionnaire partagé `pipe` :

```python
pipe = {
    "id_badge": int,        # ID du badge scanné
    "name": str,            # Nom de l'utilisateur
    "surname": str,         # Prénom
    "inside": bool | None,  # True=entrée, False=sortie, None=pas encore choisi
    "log": list[dict],      # 5 derniers pointages
    "cancel": bool,         # Annulation (timeout ou bouton)
    "quit": bool,           # Fermeture de l'app
    "new_user_valid": bool, # Nouveau badge validé
    "th_condition": Condition, # Synchronisation des threads
    # + time_current_week, time_last_week, day_current_week, day_last_week
}
```

La synchronisation utilise `threading.Condition` : `main.py` attend avec `wait()`, `view.py` notifie avec `notify_all()` quand l'utilisateur fait un choix.

## Scènes de l'interface (view.py)

```mermaid
stateDiagram-v2
    [*] --> SceneWait

    SceneWait --> SceneSelect : badge connu
    SceneWait --> SceneModal_unknown : badge inconnu

    SceneSelect --> SceneLog : bouton historique
    SceneSelect --> SceneWait : bouton annuler / timeout

    SceneLog --> SceneSelect : bouton retour
    SceneLog --> SceneWorkTime_current : bouton détail

    SceneWorkTime_current --> SceneLog : bouton retour
    SceneWorkTime_current --> SceneWorkTime_last : bouton semaine précédente

    SceneWorkTime_last --> SceneWorkTime_current : bouton retour

    SceneModal_unknown --> SceneKeyboard : confirmation
    SceneKeyboard --> SceneModal_prenom : validation nom
    SceneModal_prenom --> SceneKeyboard : confirmation
    SceneKeyboard --> SceneModal_confirm : validation prénom
    SceneModal_confirm --> SceneWait : confirmation

    SceneSelect --> SceneWait : choix Entrée/Sortie
```

Toutes les scènes avec timer (`SceneTime`) reviennent automatiquement à `SceneWait` après 1 minute d'inactivité.

## Base de données

### Tables principales

| Table | Rôle |
|-------|------|
| `user_sync` | Utilisateurs synchronisés depuis le serveur |
| `user_write` | Utilisateurs créés localement (badge inconnu) |
| `badge_sync` | Badges synchronisés depuis le serveur |
| `badge_write` | Badges créés localement |
| `log_sync` | Pointages synchronisés depuis le serveur |
| `log_write` | Pointages créés localement |

### Vues

| Vue | Rôle |
|-----|------|
| `user` | Union de `user_sync` et `user_write` (sans doublons) |
| `badge` | Union de `badge_sync` et `badge_write` (sans doublons) |
| `log` | Union de `log_sync` et `log_write` (sans doublons, triés par date) |

### Principe sync/write

Les tables `_write` stockent les données créées localement. Les tables `_sync` contiennent les données provenant du serveur distant. Les vues fusionnent les deux en éliminant les doublons. Après synchronisation, les procédures `delete_*_write` nettoient les entrées locales déjà synchronisées.

### Procédures stockées

| Procédure | Rôle |
|-----------|------|
| `insert_log` | Insère un pointage local + nettoyage |
| `insert_sync_log` | Insère un pointage depuis le serveur |
| `insert_user` / `insert_user_sync` | Insère un utilisateur local / depuis serveur |
| `insert_badge` / `insert_badge_sync` | Insère un badge local / depuis serveur |
| `delete_log_write` / `delete_badge_write` / `delete_user_write` | Nettoyage des tables locales après sync |
| `delete_badge_and_user_write` | Nettoyage combiné badges + utilisateurs |

## Synchronisation avec le serveur distant

`api_client.py` communique avec `https://timbreuse.sectioninformatique.ch` via des requêtes HTTP GET/PUT authentifiées par HMAC-SHA256 (clé dans `.key.json`).

```mermaid
sequenceDiagram
    participant T as Timbreuse (local)
    participant S as Serveur distant

    T->>S: PUT badges/utilisateurs locaux
    T->>S: PUT logs locaux
    S-->>T: GET nouveaux utilisateurs
    S-->>T: GET nouveaux badges
    S-->>T: GET nouveaux logs
    T->>T: Nettoyage tables _write
```

## Développement sur Windows

Sur Windows (`os.name == 'nt'`) :
- `fake_rfid.py` est chargé automatiquement à la place de `rfid.py` (badge simulé ID 63)
- La fenêtre Pygame s'ouvre en mode fenêtré (800x480) au lieu du plein écran
- Le curseur de la souris reste visible
- MariaDB tourne dans un container Docker
