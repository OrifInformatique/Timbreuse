#!/usr/bin/env python
from __future__ import annotations

import argparse
import datetime as dt
import os

import mariadb

DEFAULT_DB = "timbreuse2022"
DEFAULT_BADGE_ID = 900000000001
DEFAULT_USER_ID = 91001
DEFAULT_NAME = "Integration"
DEFAULT_SURNAME = "BadgeDeleted"


def db_params(db_name: str) -> dict:
    if os.name != "nt":
        return {"user": "root", "password": "0", "host": "localhost", "database": db_name}
    return {"user": "root", "password": "", "host": "localhost", "port": 3306, "database": db_name}


def reset_local_tables(cur: mariadb.Cursor) -> None:
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for table in ("event_log_sync", "log_sync", "badge_write", "badge_sync", "user_sync"):
        cur.execute(f"DELETE FROM {table}")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")


def ensure_local_fixtures(db_name: str, badge_id: int, user_id: int, name: str, surname: str) -> None:
    conn = mariadb.connect(**db_params(db_name))
    cur = conn.cursor()
    now = dt.datetime.now().replace(microsecond=0)
    two_hours_ago = now - dt.timedelta(hours=2)
    thirty_minutes_ago = now - dt.timedelta(minutes=30)
    try:
        cur.execute("START TRANSACTION")
        # On repart d'un etat vierge pour des tests E2E deterministes.
        reset_local_tables(cur)
        cur.execute(
            "INSERT INTO user_sync (id_user, name, surname, date_modif, date_delete) VALUES (?, ?, ?, NOW(), NULL) "
            "ON DUPLICATE KEY UPDATE name=VALUES(name), surname=VALUES(surname), date_modif=NOW(), date_delete=NULL",
            (user_id, name, surname),
        )
        cur.execute(
            "INSERT INTO badge_sync (id_badge, id_user, rowid_badge, date_modif, date_delete) VALUES (?, ?, ?, NOW(), NULL) "
            "ON DUPLICATE KEY UPDATE id_user=VALUES(id_user), date_modif=NOW(), date_delete=NULL",
            (badge_id, user_id, 1),
        )
        cur.execute(
            "INSERT INTO badge_write (id_badge, id_user) VALUES (?, ?) ON DUPLICATE KEY UPDATE id_user=VALUES(id_user)",
            (badge_id, user_id),
        )
        cur.execute(
            "INSERT INTO log_sync (date, id_badge, inside, id_log, id_user, date_badge, date_modif, date_delete) "
            "VALUES (?, ?, 1, ?, ?, ?, NOW(), NULL) ON DUPLICATE KEY UPDATE date=VALUES(date), id_badge=VALUES(id_badge), "
            "inside=VALUES(inside), id_user=VALUES(id_user), date_badge=VALUES(date_badge), date_modif=NOW(), date_delete=NULL",
            (two_hours_ago, badge_id, 1, user_id, two_hours_ago),
        )
        cur.execute(
            "INSERT INTO log_sync (date, id_badge, inside, id_log, id_user, date_badge, date_modif, date_delete) "
            "VALUES (?, ?, 0, ?, ?, ?, NOW(), NULL) ON DUPLICATE KEY UPDATE date=VALUES(date), id_badge=VALUES(id_badge), "
            "inside=VALUES(inside), id_user=VALUES(id_user), date_badge=VALUES(date_badge), date_modif=NOW(), date_delete=NULL",
            (thirty_minutes_ago, badge_id, 2, user_id, thirty_minutes_ago),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Injecte des donnees E2E dans la DB locale Timbreuse.")
    parser.add_argument("--db-name", default=DEFAULT_DB)
    parser.add_argument("--badge-id", type=int, default=DEFAULT_BADGE_ID)
    parser.add_argument("--user-id", type=int, default=DEFAULT_USER_ID)
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--surname", default=DEFAULT_SURNAME)
    args = parser.parse_args()
    ensure_local_fixtures(args.db_name, args.badge_id, args.user_id, args.name, args.surname)
    print("OK - donnees E2E locales injectees.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
