# Timbreuse

Application de pointage RFID développée pour le Raspberry Pi, utilisée par l'ORIF (Section Informatique). Les utilisateurs badgent à l'entrée et à la sortie, et l'application calcule automatiquement les heures de travail.

## Stack technique

- **Python 3.9+** (compatible 3.11)
- **Pygame** — interface graphique tactile
- **MariaDB** — base de données locale
- **MFRC522** — lecteur de badges RFID (Raspberry Pi)
- **API REST** — synchronisation avec un serveur distant

## Structure du projet

```
├── main.py            # Point d'entrée, orchestre view/model/rfid
├── view.py            # Interface graphique Pygame (scènes, boutons, clavier)
├── model.py           # Accès base de données MariaDB
├── api_client.py      # Client API pour synchronisation distante
├── rfid.py            # Lecture RFID via MFRC522 (Raspberry Pi)
├── fake_rfid.py       # Mock RFID pour le développement sur PC
├── requirements.txt   # Dépendances Python
├── sql/
│   ├── createDB.sql   # Schéma de la base de données
│   ├── procedures.sql # Procédures stockées (format DELIMITER)
│   └── test_data.sql  # Données de test
├── fonts/             # Polices (LiberationSans)
├── icons/             # Icônes des boutons (format BMP)
├── img/               # Images (logo ORIF)
├── run.sh             # Script de lancement sur Raspberry Pi
└── make               # Script de build
```

## Installation (développement Windows)

### Prérequis

- Python 3.9+ installé
- Docker Desktop (pour MariaDB)

### 1. Créer le virtual environment

```bash
python -m venv timbreuse
source timbreuse/Scripts/activate   # Git Bash / MinGW
# ou
timbreuse\Scripts\activate.bat      # CMD
```

### 2. Installer les dépendances

```bash
pip install pygame pygame-vkeyboard mariadb
```

### 3. Lancer MariaDB via Docker

```bash
docker run -d --name timbreuse-db \
  -p 3306:3306 \
  -e MARIADB_ROOT_PASSWORD="" \
  -e MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1 \
  -e MARIADB_DATABASE=timbreuse2022 \
  mariadb:11.4
```

### 4. Initialiser la base de données

```bash
docker cp sql/createDB.sql timbreuse-db:/tmp/createDB.sql
docker exec timbreuse-db bash -c "mariadb -u root < /tmp/createDB.sql"

docker cp sql/procedures.sql timbreuse-db:/tmp/procedures.sql
docker exec timbreuse-db bash -c "mariadb -u root < /tmp/procedures.sql"
```

### 5. Charger les données de test (optionnel)

```bash
docker cp sql/test_data.sql timbreuse-db:/tmp/test_data.sql
docker exec timbreuse-db bash -c "mariadb -u root < /tmp/test_data.sql"
```

### 6. Lancer l'application

```bash
source timbreuse/Scripts/activate
python main.py
```

L'application détecte automatiquement Windows (`os.name == 'nt'`) et utilise `fake_rfid.py` au lieu du vrai lecteur RFID.

## Installation (Raspberry Pi)

```bash
sudo apt install mariadb-server libmariadb-dev
pip install -r requirements.txt
sudo mariadb-secure-installation
```

Lancer avec `./run.sh` ou `python main.py`.

## Utilisation

- **Écran d'attente** : affiche l'heure et le logo ORIF (rebondissant)
- **Badge détecté** : affiche le nom de l'utilisateur avec boutons Entrée/Sortie
- **Badge inconnu** : clavier virtuel pour saisir nom/prénom
- **Historique** : 5 derniers pointages, détail par jour, heures semaine courante/précédente
- **Fermer** : `Escape`, clic sur X, ou `Ctrl+C` dans le terminal

## Dépendances

| Paquet | Usage |
|--------|-------|
| [pygame](https://pypi.org/project/pygame/) | Interface graphique |
| [pygame-vkeyboard](https://pypi.org/project/pygame-vkeyboard/) | Clavier virtuel tactile |
| [mariadb](https://pypi.org/project/mariadb/) | Connecteur base de données |
| [mfrc522](https://pypi.org/project/mfrc522/) | Lecteur RFID (Raspberry Pi uniquement) |
