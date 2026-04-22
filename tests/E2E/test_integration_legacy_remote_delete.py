#!/usr/bin/env python
"""
Test d'integration "legacy" pour suppression distante badge/user.

Niveau: integration lourde (Docker + DB + API), dependante de l'environnement.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import App

LOCAL_DB_CONTAINER = "timbreuse-db"
LOCAL_DB_NAME = "timbreuse2022"
PROVIDER_DB_CONTAINER = "timbreuse-srv-mariadb-1"
PROVIDER_DB_NAME = "ci4"
PROVIDER_ROOT_PASSWORD = "root"
DEFAULT_USERNAME = "test_timbreuse"


class FakeView:
    def __init__(self) -> None:
        self.current_scene = "wait"
        self.badge_sync_error_texts: list[str] = []

    def do_badge_sync_error(self, texts: list[str]):
        self.badge_sync_error_texts = list(texts)
        self.current_scene = "wait"


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def run_cmd(command: list[str]) -> str:
    proc = subprocess.run(command, capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def docker_mariadb_exec(container: str, sql: str, database: str | None = None, root_password: str | None = None) -> str:
    cmd = ["docker", "exec", container, "mariadb", "-u", "root", "-N"]
    if root_password is not None:
        cmd.append(f"-p{root_password}")
    if database:
        cmd.append(database)
    cmd.extend(["-e", sql])
    return run_cmd(cmd)


def get_provider_user_and_badge(username: str) -> tuple[int, str, str, int]:
    sql = (
        f"USE {PROVIDER_DB_NAME}; "
        "SELECT atu.id_user, us.name, us.surname, bs.id_badge "
        "FROM user u "
        "JOIN access_tim_user atu ON atu.id_ci_user=u.id "
        "JOIN user_sync us ON us.id_user=atu.id_user "
        "LEFT JOIN badge_sync bs ON bs.id_user=us.id_user AND bs.date_delete IS NULL "
        f"WHERE u.username='{username}' AND us.date_delete IS NULL "
        "ORDER BY bs.id_badge ASC LIMIT 1;"
    )
    out = docker_mariadb_exec(PROVIDER_DB_CONTAINER, sql, root_password=PROVIDER_ROOT_PASSWORD)
    parts = out.split("\t")
    if len(parts) < 4 or not parts[3]:
        raise RuntimeError("Utilisateur fournisseur ou badge actif introuvable.")
    return int(parts[0]), parts[1], parts[2], int(parts[3])


def hard_delete_provider_user_and_badge(id_user_sync: int, badge_id: int) -> None:
    sql = (
        f"USE {PROVIDER_DB_NAME}; "
        f"DELETE FROM badge_sync WHERE id_badge={badge_id} OR id_user={id_user_sync}; "
        f"DELETE FROM user_sync WHERE id_user={id_user_sync};"
    )
    docker_mariadb_exec(PROVIDER_DB_CONTAINER, sql, root_password=PROVIDER_ROOT_PASSWORD)


def simulate_next_scan_and_assert_messages(badge_id: int, expected_user_name: str) -> None:
    app = App()
    app.HAS_REMOTE_SERVER = True
    app.pipe["id_badge"] = badge_id
    app.view = FakeView()
    app.wait_modal_ack = lambda: None
    handled = app.handle_deleted_remote_badge()
    if not handled:
        raise AssertionError("Suppression distante non detectee.")
    expected = [
        f"Ce badge n'est plus attribue a {expected_user_name}.",
        "Cette correspondance est supprimee egalement sur cet appareil.",
    ]
    if app.view.badge_sync_error_texts != expected:
        raise AssertionError(f"Messages inattendus: {app.view.badge_sync_error_texts}")


def run_scenario(username: str) -> None:
    id_user_sync, name, surname, badge_id = get_provider_user_and_badge(username)
    full_name = f"{surname} {name}".strip()
    log(f"Suppression distante de user={id_user_sync}, badge={badge_id}")
    hard_delete_provider_user_and_badge(id_user_sync, badge_id)
    simulate_next_scan_and_assert_messages(badge_id, full_name)
    log("Scenario integration legacy valide.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    args = parser.parse_args()
    raise SystemExit(0 if not run_scenario(args.username) else 0)
