#!/usr/bin/env python
from __future__ import annotations

import datetime as dt
import json
import os
import argparse
import sys
import time
from pathlib import Path
from typing import Any

import mariadb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model import Model  # noqa: E402

SERVER_DB = os.getenv("E2E_SERVER_DB", "ci4")
LOCAL_DB = os.getenv("E2E_LOCAL_DB", "timbreuse2022")
LOG_FILE = Path(__file__).resolve().parent / "logs" / "E2E_logs.txt"

BADGE_1 = 910000000001
BADGE_2 = 910000000002
BADGE_3 = 910000000003
ROWID_BADGE_1 = 9910001
ROWID_BADGE_2 = 9910002
ROWID_BADGE_3 = 9910003
USER_1 = 4
USER_2 = 5
USER_3 = 6
BASE_DATE = dt.datetime(2026, 3, 30, 8, 0, 0)


class E2EModel(Model):
    def execute_and_commit(self, sql, value: tuple = ()):
        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            try:
                return super().execute_and_commit(sql, value)
            except mariadb.OperationalError as exc:
                message = str(exc)
                if "Lock wait timeout exceeded" in message and attempt < max_attempts:
                    log_line(f"Retry DB lock timeout (tentative {attempt}/{max_attempts - 1})")
                    time.sleep(attempt)
                    continue
                raise


def apply_default_test_env() -> None:
    # Defaults for local Docker-based E2E runs; still overridable via environment.
    os.environ.setdefault("TIMBREUSE_API_BASE_URL", "http://localhost")
    os.environ.setdefault("TIMBREUSE_API_KEY_FILE", ".key.json")
    os.environ.setdefault("E2E_SERVER_DB", "ci4")
    os.environ.setdefault("E2E_SERVER_DB_USER", "root")
    os.environ.setdefault("E2E_SERVER_DB_PASSWORD", "root")
    os.environ.setdefault("E2E_SERVER_DB_HOST", "127.0.0.1")
    os.environ.setdefault("E2E_SERVER_DB_PORT", "3307")


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def server_db_params() -> dict[str, Any]:
    return {
        "user": os.getenv("E2E_SERVER_DB_USER", "root"),
        "password": os.getenv("E2E_SERVER_DB_PASSWORD", "root"),
        "host": os.getenv("E2E_SERVER_DB_HOST", "127.0.0.1"),
        "port": _int_env("E2E_SERVER_DB_PORT", 3307),
        "database": os.getenv("E2E_SERVER_DB", SERVER_DB),
    }


def local_db_params() -> dict[str, Any]:
    return {
        "user": os.getenv("E2E_LOCAL_DB_USER", "root"),
        "password": os.getenv("E2E_LOCAL_DB_PASSWORD", "" if os.name == "nt" else "0"),
        "host": os.getenv("E2E_LOCAL_DB_HOST", "127.0.0.1" if os.name == "nt" else "localhost"),
        "port": _int_env("E2E_LOCAL_DB_PORT", 3306),
        "database": os.getenv("E2E_LOCAL_DB", LOCAL_DB),
    }


def log_line(text: str) -> None:
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {text}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def reset_log_file() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as fh:
        fh.write("E2E Timbreuse logs\n==================\n")
        fh.write(f"server_db={SERVER_DB}, local_db={LOCAL_DB}\n\n")


def server_conn() -> mariadb.Connection:
    return mariadb.connect(**server_db_params())


def local_conn() -> mariadb.Connection:
    return mariadb.connect(**local_db_params())


def _table_exists(conn: mariadb.Connection, table: str) -> bool:
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = ?", (table,))
        row = cur.fetchone()
        return bool(row and int(row[0]) > 0)
    finally:
        cur.close()


def _ensure_server_event_type_table(conn: mariadb.Connection) -> None:
    cur = conn.cursor()
    try:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS event_type ("
            "id INT(11) NOT NULL AUTO_INCREMENT, "
            "type VARCHAR(32) NOT NULL, "
            "user_sync_id INT(11), "
            "badge_number BIGINT(20), "
            "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            "PRIMARY KEY (id), "
            "KEY idx_event_type_created_at (created_at), "
            "KEY idx_event_type_type (type), "
            "KEY idx_event_type_user_sync_id (user_sync_id), "
            "KEY idx_event_type_badge_number (badge_number)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        )
        conn.commit()
    finally:
        cur.close()


def _ensure_local_event_log_sync_table(conn: mariadb.Connection) -> None:
    cur = conn.cursor()
    try:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS event_log_sync ("
            "id_event INT(11) NOT NULL, "
            "event_type VARCHAR(32) NOT NULL, "
            "entity_type VARCHAR(32) NOT NULL, "
            "entity_id BIGINT(20) NOT NULL, "
            "payload TEXT, "
            "date_event DATETIME NOT NULL, "
            "processed TINYINT(1) NOT NULL DEFAULT 0, "
            "processed_at DATETIME, "
            "PRIMARY KEY (id_event), "
            "KEY idx_event_log_sync_date_event (date_event)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        )
        conn.commit()
    finally:
        cur.close()


def ensure_e2e_schema_prerequisites() -> None:
    server = server_conn()
    local = local_conn()
    try:
        _ensure_server_event_type_table(server)
        _ensure_local_event_log_sync_table(local)
        log_line("Schema E2E verifie: event_type (serveur) et event_log_sync (local).")
    finally:
        local.close()
        server.close()


def assert_required_tables() -> None:
    server_required = ["user_sync", "badge_sync", "log_sync", "event_type"]
    local_required = ["user_sync", "badge_sync", "log_sync", "badge_write", "event_log_sync"]
    server = server_conn()
    local = local_conn()
    try:
        missing_server = [table for table in server_required if not _table_exists(server, table)]
        missing_local = [table for table in local_required if not _table_exists(local, table)]
    finally:
        local.close()
        server.close()

    if not missing_server and not missing_local:
        return

    details: list[str] = []
    if missing_server:
        details.append(f"serveur={', '.join(missing_server)}")
    if missing_local:
        details.append(f"local={', '.join(missing_local)}")
    joined = " | ".join(details)
    raise RuntimeError(
        "Schema incomplet pour E2E: "
        f"{joined}. Verifie les migrations/creation de DB avant de relancer."
    )


def _reset_tables(conn: mariadb.Connection, tables: list[str], label: str) -> None:
    cur = conn.cursor()
    deleted_tables: list[str] = []
    skipped_tables: list[str] = []
    try:
        cur.execute("START TRANSACTION")
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        for table in tables:
            if _table_exists(conn, table):
                cur.execute(f"DELETE FROM {table}")
                deleted_tables.append(table)
            else:
                skipped_tables.append(table)
        cur.execute("SET FOREIGN_KEY_CHECKS=1")
        conn.commit()
        if deleted_tables:
            log_line(f"Reset DB {label} (DELETE): {', '.join(deleted_tables)}")
        if skipped_tables:
            log_line(f"Reset DB {label} (SKIP absentes): {', '.join(skipped_tables)}")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def reset_e2e_databases() -> None:
    server = server_conn()
    local = local_conn()
    try:
        # Server: uniquement les tables necessaires au scenario.
        _reset_tables(server, ["event_type", "log_sync", "badge_sync", "user_sync"], "serveur")
        # Local: etat synchronise + file d'evenements + ecriture badge.
        _reset_tables(local, ["event_log_sync", "log_sync", "badge_write", "badge_sync", "user_sync"], "local")
    finally:
        local.close()
        server.close()


def _fetch_count(conn: mariadb.Connection, query: str, params: tuple[Any, ...] = ()) -> int:
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        row = cur.fetchone()
        return int(row[0]) if row else 0
    finally:
        cur.close()


def _fetch_value(conn: mariadb.Connection, query: str, params: tuple[Any, ...] = ()) -> Any:
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        cur.close()


def _value_at_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def assert_checks(
    tag: str, snapshot: dict[str, Any], checks: list[tuple[str, str, Any]], strict: bool, failures: list[str]
) -> None:
    for path, operator, expected in checks:
        actual = _value_at_path(snapshot, path)
        if operator == "==":
            ok = actual == expected
        elif operator == ">=":
            ok = actual is not None and actual >= expected
        else:
            raise ValueError(f"Operateur non supporte: {operator}")

        if ok:
            log_line(f"PASS [{tag}] {path} {operator} {expected} (actual={actual})")
            continue

        message = f"FAIL [{tag}] {path} {operator} {expected} (actual={actual})"
        log_line(message)
        failures.append(message)
        if strict:
            raise AssertionError(message)


def db_snapshot(tag: str) -> dict[str, Any]:
    server = server_conn()
    local = local_conn()
    try:
        snapshot = {
            "server": {
                "badge1_exists": _fetch_count(server, "SELECT COUNT(*) FROM badge_sync WHERE id_badge = ?", (BADGE_1,)),
                "badge1_deleted_not_null": _fetch_count(
                    server, "SELECT COUNT(*) FROM badge_sync WHERE id_badge = ? AND date_delete IS NOT NULL", (BADGE_1,)
                ),
                "badge2_user": _fetch_value(server, "SELECT id_user FROM badge_sync WHERE id_badge = ?", (BADGE_2,)),
                "badge3_user": _fetch_value(server, "SELECT id_user FROM badge_sync WHERE id_badge = ?", (BADGE_3,)),
                "user2_exists": _fetch_count(server, "SELECT COUNT(*) FROM user_sync WHERE id_user = ?", (USER_2,)),
                "user2_soft_deleted": _fetch_count(
                    server, "SELECT COUNT(*) FROM user_sync WHERE id_user = ? AND date_delete IS NOT NULL", (USER_2,)
                ),
                "hard_delete_events_badge1": _fetch_count(
                    server,
                    "SELECT COUNT(*) FROM event_type WHERE type='hard_delete' AND badge_number=?",
                    (BADGE_1,),
                ),
                "hard_delete_events_user2": _fetch_count(
                    server,
                    "SELECT COUNT(*) FROM event_type WHERE type='hard_delete' AND user_sync_id=?",
                    (USER_2,),
                ),
            },
            "local": {
                "badge1_exists": _fetch_count(local, "SELECT COUNT(*) FROM badge_sync WHERE id_badge = ?", (BADGE_1,)),
                "badge1_deleted_not_null": _fetch_count(
                    local, "SELECT COUNT(*) FROM badge_sync WHERE id_badge = ? AND date_delete IS NOT NULL", (BADGE_1,)
                ),
                "badge2_user": _fetch_value(local, "SELECT id_user FROM badge_sync WHERE id_badge = ?", (BADGE_2,)),
                "badge3_user": _fetch_value(local, "SELECT id_user FROM badge_sync WHERE id_badge = ?", (BADGE_3,)),
                "user2_exists": _fetch_count(local, "SELECT COUNT(*) FROM user_sync WHERE id_user = ?", (USER_2,)),
                "user2_soft_deleted": _fetch_count(
                    local, "SELECT COUNT(*) FROM user_sync WHERE id_user = ? AND date_delete IS NOT NULL", (USER_2,)
                ),
                "event_log_user2_received": _fetch_count(
                    local,
                    "SELECT COUNT(*) FROM event_log_sync WHERE entity_type='user' AND entity_id=? AND event_type='hard_delete'",
                    (USER_2,),
                ),
                "event_log_user2_processed": _fetch_count(
                    local,
                    "SELECT COUNT(*) FROM event_log_sync WHERE entity_type='user' AND entity_id=? AND event_type='hard_delete' AND processed=1",
                    (USER_2,),
                ),
            },
        }
        log_line(f"Snapshot DB [{tag}] | {json.dumps(snapshot, ensure_ascii=False)}")
        return snapshot
    finally:
        local.close()
        server.close()


def ensure_server_fixtures() -> None:
    conn = server_conn()
    cur = conn.cursor()
    try:
        cur.execute("START TRANSACTION")
        for user_id, name, surname in (
            (USER_1, "Integration", "E2E_User1"),
            (USER_2, "Integration", "E2E_User2"),
            (USER_3, "Integration", "E2E_User3"),
        ):
            cur.execute(
                "INSERT INTO user_sync (id_user, name, surname, date_modif, date_delete) VALUES (?, ?, ?, NOW(), NULL) "
                "ON DUPLICATE KEY UPDATE name=VALUES(name), surname=VALUES(surname), date_modif=NOW(), date_delete=NULL",
                (user_id, name, surname),
            )

        for badge_id, user_id, rowid in (
            (BADGE_1, USER_1, ROWID_BADGE_1),
            (BADGE_2, None, ROWID_BADGE_2),
            (BADGE_3, USER_2, ROWID_BADGE_3),
        ):
            cur.execute(
                "INSERT INTO badge_sync (id_badge, id_user, rowid_badge, date_modif, date_delete) VALUES (?, ?, ?, NOW(), NULL) "
                "ON DUPLICATE KEY UPDATE id_user=VALUES(id_user), date_modif=NOW(), date_delete=NULL",
                (badge_id, user_id, rowid),
            )

        # Jeu de donnees minimal: juste ce qui est necessaire au scenario et aux scans.
        for idx in range(2):
            when = BASE_DATE + dt.timedelta(hours=idx)
            cur.execute(
                "INSERT INTO log_sync (`date`, id_badge, inside, id_user, date_badge, date_modif, date_delete) VALUES (?, ?, ?, ?, ?, NOW(), NULL)",
                (when, BADGE_1, idx % 2, USER_1, when),
            )
        for idx in range(2):
            when = BASE_DATE + dt.timedelta(hours=idx)
            cur.execute(
                "INSERT INTO log_sync (`date`, id_badge, inside, id_user, date_badge, date_modif, date_delete) VALUES (?, ?, ?, ?, ?, NOW(), NULL)",
                (when, BADGE_3, idx % 2, USER_2, when),
            )
        conn.commit()
        log_line("Fixtures serveur initialisees (users/badges/logs).")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def sync_from_server() -> None:
    model = E2EModel()
    log_line("Sync: debut invoke_receive_event_logs")
    model.invoke_receive_event_logs()
    log_line("Sync: fin invoke_receive_event_logs")
    log_line("Sync: debut apply_event_logs")
    model.apply_event_logs()
    log_line("Sync: fin apply_event_logs")
    log_line("Sync: debut invoke_receive_users")
    model.invoke_receive_users()
    log_line("Sync: fin invoke_receive_users")
    log_line("Sync: debut invoke_receive_badges")
    model.invoke_receive_badges()
    log_line("Sync: fin invoke_receive_badges")
    log_line("Sync: debut invoke_receive_logs")
    model.invoke_receive_logs()
    log_line("Sync: fin invoke_receive_logs")
    log_line("Sync: debut delete_badges_and_users_local")
    model.delete_badges_and_users_local()
    log_line("Sync: fin delete_badges_and_users_local")
    log_line("Synchronisation serveur -> timbreuse terminee.")


def simulate_scan_local(badge_id: int) -> dict[str, Any]:
    conn = local_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_user, date_delete FROM badge_sync WHERE id_badge = ?", (badge_id,))
        row = cur.fetchone()
        if row is None:
            return {"badge_id": badge_id, "status": "badge_inconnu", "user_id": None, "logs_count": 0}
        user_id, badge_deleted = row
        if badge_deleted is not None:
            return {"badge_id": badge_id, "status": "badge_supprime", "user_id": user_id, "logs_count": 0}
        if user_id is None:
            return {"badge_id": badge_id, "status": "badge_non_attribue", "user_id": None, "logs_count": 0}
        cur.execute("SELECT COUNT(*) FROM log_sync WHERE id_user = ? AND date_delete IS NULL", (int(user_id),))
        return {"badge_id": badge_id, "status": "ok", "user_id": int(user_id), "logs_count": int(cur.fetchone()[0])}
    finally:
        cur.close()
        conn.close()


def server_hard_delete_badge_1() -> None:
    conn = server_conn()
    cur = conn.cursor()
    try:
        cur.execute("START TRANSACTION")
        cur.execute("UPDATE badge_sync SET id_user=NULL, date_delete=NOW(), date_modif=NOW() WHERE id_badge=?", (BADGE_1,))
        cur.execute("INSERT INTO event_type (type, user_sync_id, badge_number) VALUES ('hard_delete', NULL, ?)", (BADGE_1,))
        conn.commit()
        log_line("Etape 1: hard delete badge 1 + event_type.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def server_soft_delete_user_2_and_reassign_badge_3() -> None:
    conn = server_conn()
    cur = conn.cursor()
    try:
        cur.execute("START TRANSACTION")
        cur.execute("UPDATE user_sync SET date_delete=NOW(), date_modif=NOW() WHERE id_user=?", (USER_2,))
        cur.execute("UPDATE badge_sync SET id_user=?, date_delete=NULL, date_modif=NOW() WHERE id_badge=?", (USER_1, BADGE_2))
        cur.execute("UPDATE badge_sync SET id_user=?, date_delete=NULL, date_modif=NOW() WHERE id_badge=?", (USER_3, BADGE_3))
        when_1 = BASE_DATE + dt.timedelta(days=7, hours=8)
        when_2 = BASE_DATE + dt.timedelta(days=7, hours=17)
        cur.execute(
            "INSERT INTO log_sync (`date`, id_badge, inside, id_user, date_badge, date_modif, date_delete) VALUES (?, ?, ?, ?, ?, NOW(), NULL)",
            (when_1, BADGE_2, 1, USER_1, when_1),
        )
        cur.execute(
            "INSERT INTO log_sync (`date`, id_badge, inside, id_user, date_badge, date_modif, date_delete) VALUES (?, ?, ?, ?, ?, NOW(), NULL)",
            (when_2, BADGE_2, 0, USER_1, when_2),
        )
        conn.commit()
        log_line("Etape 2: soft delete user2 + reattribution badge2->user1 et badge3->user3.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def _server_delete_user_fk_dependents(cur: mariadb.Cursor, user_id: int) -> None:
    cur.execute(
        "SELECT TABLE_NAME, COLUMN_NAME "
        "FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE REFERENCED_TABLE_SCHEMA = DATABASE() "
        "AND REFERENCED_TABLE_NAME = 'user_sync' "
        "AND REFERENCED_COLUMN_NAME = 'id_user' "
        "AND TABLE_NAME <> 'user_sync'"
    )
    dependencies = cur.fetchall() or []
    cleaned: list[str] = []
    for table_name, column_name in dependencies:
        # Nettoyage generique des references FK vers user_sync.id_user.
        sql = f"DELETE FROM `{table_name}` WHERE `{column_name}`=?"
        cur.execute(sql, (user_id,))
        if cur.rowcount and cur.rowcount > 0:
            cleaned.append(f"{table_name}.{column_name}={cur.rowcount}")
    if cleaned:
        log_line(f"Etape 4 pre-clean FK user2: {', '.join(cleaned)}")
    else:
        log_line("Etape 4 pre-clean FK user2: aucune dependance a supprimer.")


def server_hard_delete_user_2() -> None:
    conn = server_conn()
    cur = conn.cursor()
    try:
        cur.execute("START TRANSACTION")
        _server_delete_user_fk_dependents(cur, USER_2)
        cur.execute("DELETE FROM user_sync WHERE id_user=?", (USER_2,))
        cur.execute("INSERT INTO event_type (type, user_sync_id, badge_number) VALUES ('hard_delete', ?, NULL)", (USER_2,))
        conn.commit()
        log_line("Etape 4: hard delete user2 + event_type.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def verify_local_event_processed_for_user_2() -> bool:
    conn = local_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT COUNT(*) FROM event_log_sync WHERE entity_type='user' AND entity_id=? AND event_type='hard_delete' AND processed=1",
            (USER_2,),
        )
        return int(cur.fetchone()[0]) > 0
    finally:
        cur.close()
        conn.close()


def run_all(strict: bool) -> None:
    failures: list[str] = []
    apply_default_test_env()
    reset_log_file()
    mode = "strict" if strict else "non-strict"
    log_line(f"Debut scenario E2E (mode={mode}).")
    ensure_e2e_schema_prerequisites()
    assert_required_tables()
    reset_e2e_databases()
    ensure_server_fixtures()
    sync_from_server()
    snap = db_snapshot("apres_fixture_et_sync_initiale")
    assert_checks(
        "apres_fixture_et_sync_initiale",
        snap,
        [
            ("server.badge1_exists", "==", 1),
            ("server.badge1_deleted_not_null", "==", 0),
            ("server.badge3_user", "==", USER_2),
            ("server.user2_exists", "==", 1),
            ("server.user2_soft_deleted", "==", 0),
            ("local.badge1_exists", "==", 1),
            ("local.badge1_deleted_not_null", "==", 0),
            ("local.badge3_user", "==", USER_2),
            ("local.user2_exists", "==", 1),
            ("local.user2_soft_deleted", "==", 0),
            ("local.event_log_user2_processed", "==", 0),
        ],
        strict,
        failures,
    )
    log_line(f"Pre-suppression scan badge1 | {json.dumps(simulate_scan_local(BADGE_1), ensure_ascii=False)}")
    log_line(f"Pre-suppression scan badge2 | {json.dumps(simulate_scan_local(BADGE_2), ensure_ascii=False)}")
    log_line(f"Pre-suppression scan badge3 | {json.dumps(simulate_scan_local(BADGE_3), ensure_ascii=False)}")
    server_hard_delete_badge_1()
    sync_from_server()
    snap = db_snapshot("apres_etape1_hard_delete_badge1")
    assert_checks(
        "apres_etape1_hard_delete_badge1",
        snap,
        [
            ("server.badge1_exists", "==", 1),
            ("server.badge1_deleted_not_null", "==", 1),
            ("server.hard_delete_events_badge1", ">=", 1),
            ("local.badge1_exists", "==", 1),
            ("local.badge1_deleted_not_null", "==", 1),
        ],
        strict,
        failures,
    )
    server_soft_delete_user_2_and_reassign_badge_3()
    sync_from_server()
    snap = db_snapshot("apres_etape2_soft_delete_user2_reattrib_badge3")
    assert_checks(
        "apres_etape2_soft_delete_user2_reattrib_badge3",
        snap,
        [
            ("server.user2_exists", "==", 1),
            ("server.user2_soft_deleted", "==", 1),
            ("server.badge2_user", "==", USER_1),
            ("server.badge3_user", "==", USER_3),
            ("local.user2_exists", "==", 1),
            ("local.user2_soft_deleted", "==", 1),
            ("local.badge2_user", "==", USER_1),
            ("local.badge3_user", "==", USER_3),
        ],
        strict,
        failures,
    )
    step3_badge2 = simulate_scan_local(BADGE_2)
    log_line(f"Etape3 scan badge2 | {json.dumps(step3_badge2, ensure_ascii=False)}")
    step3 = simulate_scan_local(BADGE_3)
    log_line(f"Etape3 scan badge3 | {json.dumps(step3, ensure_ascii=False)}")
    server_hard_delete_user_2()
    sync_from_server()
    snap = db_snapshot("apres_etape4_hard_delete_user2")
    assert_checks(
        "apres_etape4_hard_delete_user2",
        snap,
        [
            ("server.user2_exists", "==", 0),
            ("server.hard_delete_events_user2", ">=", 1),
            # Le hard delete distant est applique localement comme soft delete.
            ("local.user2_exists", "==", 1),
            ("local.user2_soft_deleted", "==", 1),
            ("local.event_log_user2_received", ">=", 1),
            ("local.event_log_user2_processed", ">=", 1),
            ("local.badge2_user", "==", USER_1),
            ("local.badge3_user", "==", USER_3),
        ],
        strict,
        failures,
    )
    step5_badge2 = simulate_scan_local(BADGE_2)
    log_line(f"Etape5 scan badge2 | {json.dumps(step5_badge2, ensure_ascii=False)}")
    log_line(f"Verification event_log_sync processed=1 pour user2: {verify_local_event_processed_for_user_2()}")
    step5 = simulate_scan_local(BADGE_3)
    log_line(f"Etape5 scan badge3 | {json.dumps(step5, ensure_ascii=False)}")
    if failures:
        log_line(f"E2E FAIL - {len(failures)} assertion(s) en echec.")
        raise AssertionError(f"{len(failures)} assertion(s) en echec. Voir {LOG_FILE}")
    log_line("E2E PASS - toutes les assertions sont valides.")
    log_line("Fin scenario E2E.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scenario E2E Timbreuse avec validations SQL.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--strict", action="store_true", help="Arrete le scenario au 1er echec d'assertion (defaut).")
    mode_group.add_argument("--non-strict", action="store_true", help="Continue malgre les echecs et echoue a la fin.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        run_all(strict=not args.non_strict)
    except Exception as exc:
        log_line(f"E2E FAIL - {exc}")
        raise
