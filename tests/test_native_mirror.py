import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "littlepowers_mirror.py"
spec = importlib.util.spec_from_file_location("mirror", SCRIPT)
mirror = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mirror)


class NativeMirrorTests(unittest.TestCase):
    def data(self, host="claude"):
        return {"workflow": "12345678-1234-4234-8234-123456789abc",
                "host": host, "session": "session-one/list-one",
                "tools": ["TaskCreate", "TaskGet", "TaskList", "TaskUpdate"],
                "tasks": [{"id": "T1", "title": "Implement", "status": "pending"},
                          {"id": "T2", "title": "Verify", "status": "pending"}],
                "observed": [], "receipt": None}

    def synced(self, host="claude", tools=None):
        data = self.data(host)
        if tools is not None:
            data["tools"] = tools
        first = mirror.project(data)
        observed = [dict(row, native_id=str(i)) for i, row in enumerate(first["desired"], 1)]
        data["observed"] = copy.deepcopy(observed)
        data["receipt"] = {"scope": first["scope"], "backend": first["backend"], "rows": observed}
        return data

    def test_host_capabilities_not_version_assumptions(self):
        profiles = [("codex", ["update_plan"], "update_plan"),
                    ("claude", self.data()["tools"], "tasks"),
                    ("qoder", self.data()["tools"], "tasks"),
                    ("claude", ["TodoWrite"], "TodoWrite"),
                    ("qoder", ["TodoWrite"], "TodoWrite"),
                    ("opencode", ["todowrite"], "todowrite")]
        for host, tools, backend in profiles:
            with self.subTest(host=host, backend=backend):
                data = self.data(host)
                data["tools"] = tools
                self.assertEqual(mirror.project(data)["backend"], backend)
                self.assertEqual(mirror.project(data)["status"], "ready")

    def test_unavailable_and_unknown_list_never_generate_operations(self):
        for tools, observed in [([], []), (["TaskCreate"], []), (self.data()["tools"], None)]:
            data = self.data()
            data.update(tools=tools, observed=observed)
            result = mirror.project(data)
            self.assertEqual(result["status"], "unavailable")
            self.assertEqual(result["operations"], [])

    def test_create_stable_keys_and_no_mutation(self):
        data = self.data()
        original = copy.deepcopy(data)
        result = mirror.project(data)
        self.assertEqual([x["action"] for x in result["operations"]], ["create", "create"])
        self.assertTrue(result["desired"][0]["key"].endswith(":T1"))
        self.assertEqual(data, original)

    def test_resume_is_noop_and_status_update_targets_original_id(self):
        data = self.synced()
        self.assertEqual(mirror.project(data)["status"], "noop")
        data["tasks"][0]["status"] = "in_progress"
        operations = mirror.project(data)["operations"]
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0]["action"], "update")
        self.assertEqual(operations[0]["row"]["native_id"], "1")

    def test_unrelated_task_preserved(self):
        data = self.synced()
        data["observed"].append({"key": None, "native_id": "other", "title": "User task", "status": "pending"})
        data["tasks"][0]["status"] = "completed"
        self.assertEqual(len(mirror.project(data)["operations"]), 1)

    def test_manual_edits_deletion_and_id_changes_conflict(self):
        for change in ("title", "status", "native_id", "delete"):
            with self.subTest(change=change):
                data = self.synced()
                if change == "delete":
                    data["observed"].pop()
                else:
                    data["observed"][0][change] = "completed" if change == "status" else "changed"
                result = mirror.project(data)
                self.assertEqual(result["status"], "conflict")
                self.assertEqual(result["operations"], [])

    def test_lost_receipt_adopts_only_exact_rows(self):
        data = self.synced()
        data["receipt"] = None
        self.assertEqual(mirror.project(data)["status"], "noop")
        data["tasks"][0]["status"] = "completed"
        self.assertEqual(mirror.project(data)["status"], "conflict")

    def test_task_removal_does_not_delete_native_work(self):
        data = self.synced()
        data["tasks"].pop()
        self.assertEqual(mirror.project(data)["status"], "conflict")

    def test_receipt_scope_and_backend_are_exact(self):
        for key in ("workflow", "host", "session"):
            data = self.synced()
            data["receipt"]["scope"][key] = "other"
            with self.assertRaises(ValueError):
                mirror.project(data)
        data = self.synced()
        data["receipt"]["backend"] = "TodoWrite"
        with self.assertRaises(ValueError):
            mirror.project(data)

    def test_bulk_replacement_requires_entire_list_ownership(self):
        data = self.synced("codex", ["update_plan"])
        self.assertEqual(mirror.project(data)["status"], "noop")
        data["tasks"][0]["status"] = "completed"
        self.assertEqual(mirror.project(data)["operations"][0]["action"], "replace")
        data["observed"].append({"key": None, "title": "Not ours", "status": "pending"})
        self.assertEqual(mirror.project(data)["status"], "conflict")

    def test_invalid_duplicate_ids_and_multiple_active_tasks(self):
        cases = []
        data = self.data(); data["tasks"][1]["id"] = "T1"; cases.append(data)
        data = self.data(); data["tasks"][0]["status"] = "done"; cases.append(data)
        data = self.data()
        for row in data["tasks"]: row["status"] = "in_progress"
        cases.append(data)
        data = self.synced(); data["observed"].append(data["observed"][0]); cases.append(data)
        data = self.synced(); data["observed"][1]["native_id"] = "1"; cases.append(data)
        data = self.data(); data["workflow"] = "not-a-uuid"; cases.append(data)
        data = self.data(); data["tasks"][0]["id"] = 1; cases.append(data)
        for value in cases:
            with self.assertRaises(ValueError): mirror.project(value)

    def test_partial_success_only_creates_remaining_rows(self):
        data = self.synced()
        data["observed"].pop()
        data["receipt"]["rows"].pop()
        operations = mirror.project(data)["operations"]
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0]["row"]["key"].split(":")[-1], "T2")

    def test_cli_bounded_input_and_malformed_json(self):
        for payload in (b"{", b" " * (mirror.MAX_BYTES + 1)):
            process = subprocess.run([sys.executable, str(SCRIPT)], input=payload, capture_output=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(json.loads(process.stdout)["operations"], [])
        process = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(self.data()).encode(), capture_output=True)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(json.loads(process.stdout)["status"], "ready")

    def test_all_applicable_routes_link_shared_reference(self):
        for skill in ("using-littlepowers", "writing-plans", "compact-shaping", "executing-plans"):
            body = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../../references/native-task-mirror.md", body)
        reference = ROOT / "references" / "native-task-mirror.md"
        self.assertTrue(reference.is_file())


if __name__ == "__main__":
    unittest.main()
