# Schéma de base de données — Timbreuse

## Diagramme relationnel

```mermaid
erDiagram
    user_sync ||--o{ badge_sync : "id_user"
    user_sync ||--o{ log_sync : "id_user"
    badge_sync ||--o{ log_sync : "id_badge"

    user_sync {
        INT id_user PK
        TEXT name
        TEXT surname
        DATETIME date_modif
        DATETIME date_delete
    }

    user_write {
        INT id_user PK "AUTO_INCREMENT"
        TEXT name
        TEXT surname
    }

    badge_sync {
        BIGINT id_badge PK
        INT id_user FK
        INT rowid_badge UK
        DATETIME date_modif
        DATETIME date_delete
    }

    badge_write {
        BIGINT id_badge PK
        INT id_user
    }

    log_sync {
        INT id_log PK
        DATETIME date
        BIGINT id_badge FK
        BOOL inside
        INT id_user FK
        DATETIME date_badge
        DATETIME date_modif
        DATETIME date_delete
    }

    log_write {
        INT id_log PK "AUTO_INCREMENT"
        DATETIME date
        BIGINT id_badge
        BOOL inside
    }
```

## Vues (fusion sync + write)

```mermaid
graph LR
    subgraph Vues
        user_view["vue user"]
        badge_view["vue badge"]
        log_view["vue log"]
    end

    user_sync -->|UNION| user_view
    user_write -->|UNION| user_view

    badge_sync -->|UNION| badge_view
    badge_write -->|UNION| badge_view

    log_sync -->|UNION| log_view
    log_write -->|UNION| log_view
```

Les vues éliminent les doublons : si une entrée existe dans `_sync`, l'entrée correspondante dans `_write` est ignorée.

## Cycle de vie des données

```mermaid
sequenceDiagram
    participant Badge as Badge RFID
    participant App as Application
    participant LW as log_write
    participant API as Serveur distant
    participant LS as log_sync

    Badge->>App: Scan badge
    App->>LW: INSERT (date, id_badge, inside)
    App->>API: PUT log
    API-->>App: GET nouveaux logs
    App->>LS: INSERT (depuis serveur)
    App->>LW: DELETE doublons avec log_sync
```

## Initialisation

```bash
# Créer la base et les tables
docker exec timbreuse-db bash -c "mariadb -u root < /tmp/createDB.sql"

# Créer les procédures stockées
docker exec timbreuse-db bash -c "mariadb -u root < /tmp/procedures.sql"

# Charger les données de test
docker exec timbreuse-db bash -c "mariadb -u root < /tmp/test_data.sql"
```

## Données de test

Le fichier `sql/test_data.sql` contient :
- 3 utilisateurs (Dupont Jean, Martin Sophie, Müller Hans)
- 3 badges (dont le badge 63 utilisé par `fake_rfid.py`)
- Des logs sur 2 semaines pour tester l'affichage des heures
