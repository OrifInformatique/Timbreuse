#!/usr/bin/env python
"""
Tests metier de App.handle_deleted_remote_badge() avec un mock timbreuse-srv.

Niveau: unitaire/rapide (stable, sans Docker/DB/API reelle).
"""

import sys
import types
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Injection de modules factices pour importer main.py sans dependances lourdes
fake_view_module = types.ModuleType("view")


class _FakeViewClass:
    def __init__(self):
        self.current_scene = "wait"

    def load(self):
        return None

    def read_pipe(self, _pipe):
        return None


fake_view_module.View = _FakeViewClass
sys.modules["view"] = fake_view_module

fake_model_module = types.ModuleType("model")


class _FakeModelClass:
    pass


fake_model_module.Model = _FakeModelClass
sys.modules["model"] = fake_model_module

from main import App


class MockTimbreuseSrv:
    def __init__(self):
        self._active_badges = {}

    def assign_badge(self, badge_id: int, user_id: int) -> None:
        self._active_badges[badge_id] = user_id

    def remote_user_exists_for_badge(self, badge_id: int) -> bool:
        return badge_id in self._active_badges


class MockModel:
    def __init__(self, remote_srv: MockTimbreuseSrv):
        self.remote_srv = remote_srv
        self.local_mapping = {}
        self.removed_badges = []

    def set_local_mapping(self, badge_id: int, user_name: str) -> None:
        self.local_mapping[badge_id] = user_name

    def check_badge_assignment_with_remote(self, badge_id: int) -> dict:
        local_name = self.local_mapping.get(badge_id, "")
        return {
            "remote_exists": self.remote_srv.remote_user_exists_for_badge(badge_id),
            "local_exists": badge_id in self.local_mapping,
            "local_user_name": local_name,
        }

    def remove_local_badge_correspondance(self, badge_id: int) -> None:
        self.removed_badges.append(badge_id)
        self.local_mapping.pop(badge_id, None)


class MockView:
    def __init__(self):
        self.current_scene = "wait"
        self.modal_texts = None

    def do_badge_sync_error(self, texts):
        self.modal_texts = list(texts)
        self.current_scene = "modal"


def build_app_for_test(model: MockModel, view: MockView, badge_id: int):
    app = App.__new__(App)
    app.model = model
    app.view = view
    app.pipe = {"id_badge": badge_id, "quit": False}
    app._wait_modal_ack_called = 0

    def _fake_wait_modal_ack():
        app._wait_modal_ack_called += 1
        app.view.current_scene = "wait"

    app.wait_modal_ack = _fake_wait_modal_ack
    return app


class TestHandleDeletedRemoteBadgeMock(unittest.TestCase):
    def setUp(self):
        self.badge_id = 424242
        self.remote_srv = MockTimbreuseSrv()
        self.model = MockModel(self.remote_srv)
        self.view = MockView()

    def test_remote_exists_no_action(self):
        self.remote_srv.assign_badge(self.badge_id, user_id=10)
        self.model.set_local_mapping(self.badge_id, "Doe John")
        app = build_app_for_test(self.model, self.view, self.badge_id)
        handled = app.handle_deleted_remote_badge()
        self.assertFalse(handled)

    def test_remote_deleted_local_exists_shows_expected_texts(self):
        self.model.set_local_mapping(self.badge_id, "Doe John")
        app = build_app_for_test(self.model, self.view, self.badge_id)
        handled = app.handle_deleted_remote_badge()
        self.assertTrue(handled)
        self.assertEqual(self.model.removed_badges, [self.badge_id])


if __name__ == "__main__":
    unittest.main(verbosity=2)
