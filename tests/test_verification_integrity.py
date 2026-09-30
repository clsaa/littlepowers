from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

import test_outcome_gates as gate_fixture
from test_outcome_gates import block, contract_record
import littlepowers_state as state_module


class VerificationIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = gate_fixture.OutcomeGateTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root = self.fixture.root

    def ready(self):
        return self.fixture.ready_for_verify()

    def recorded(self):
        return self.fixture.record_verification(self.ready())

    def finish(self, state):
        return state_module.command_finish(self.fixture.writer(state), self.root, "complete")

    def assert_atomic_failure(self, action, pattern):
        before = state_module.state_path(self.root).read_bytes()
        with self.assertRaisesRegex(state_module.StateError, pattern):
            action()
        self.assertEqual(state_module.state_path(self.root).read_bytes(), before)

    def set_inputs(self, inputs):
        record = state_module.parse_outcome_verification(self.fixture.evidence_path.read_text())
        if inputs is None:
            record.pop("inputs", None)
        else:
            record["inputs"] = inputs
        self.fixture.evidence_path.write_text(block("verification", record))

    def capture(self, files=None, absent=None, manual_reason=None):
        return state_module.capture_verification_inputs(
            self.root, files=files or [], absent=absent or [], manual_reason=manual_reason,
        )

    def test_plan_prose_drift_blocks_recording_atomically(self):
        state = self.ready()
        self.fixture.plan_path.write_text(self.fixture.plan_path.read_text() + "\nExecute unapproved work.\n")
        self.assert_atomic_failure(lambda: self.fixture.record_verification(state), "artifact bytes")

    def test_plan_prose_drift_blocks_completion_and_writer_atomically(self):
        state = self.recorded()
        self.fixture.plan_path.write_text(self.fixture.plan_path.read_text() + "\nExecute unapproved work.\n")
        self.assert_atomic_failure(lambda: self.finish(state), "artifact bytes")
        forged = copy.deepcopy(state)
        forged["status"] = "complete"
        self.assert_atomic_failure(lambda: state_module.write_state(self.root, forged), "artifact bytes")

    def test_current_plan_path_must_still_match_approval(self):
        state = self.recorded()
        (self.root / "docs/plans/copied.md").write_bytes(self.fixture.plan_path.read_bytes())
        state["artifacts"]["plan"] = "docs/plans/copied.md"
        # Pure gate sees this in-memory candidate; command_finish reloads disk.
        self.assertTrue(any("current artifact path" in x for x in state_module.completion_gate_failures(self.root, state)))
        state["status"] = "complete"
        self.assert_atomic_failure(lambda: state_module.write_state(self.root, state), "current artifact path")

    def test_checkpoint_cannot_replace_current_plan_path(self):
        state = self.recorded()
        (self.root / "docs/plans/copied.md").write_bytes(self.fixture.plan_path.read_bytes())
        self.assert_atomic_failure(
            lambda: self.fixture.checkpoint(state, artifact=["plan=docs/plans/copied.md"]),
            "require validate-plan",
        )

    def test_embedded_plan_sources_are_rechecked_at_both_boundaries(self):
        extra = self.root / "docs/product/plan-source.txt"
        extra.write_text("Approved plan input\n")
        contract = contract_record()
        contract["sources"][0]["path"] = "docs/product/plan-source.txt"
        self.fixture.plan_path.write_text(self.fixture.plan_path.read_text() + block("contract", contract))
        state = self.ready()
        extra.write_text("Unapproved change\n")
        self.assert_atomic_failure(lambda: self.fixture.record_verification(state), "contract sources")
        extra.write_text("Approved plan input\n")
        state = self.fixture.record_verification(state)
        extra.write_text("Unapproved change\n")
        self.assert_atomic_failure(lambda: self.finish(state), "contract sources")

    def test_missing_consumption_cannot_complete(self):
        state = self.recorded()
        state["review"]["last_resolution"]["consumption"]["plan_validation_revision"] = None
        self.assertTrue(any("not consumed" in x for x in state_module.completion_gate_failures(self.root, state)))

    def test_input_change_between_capture_and_record_is_atomic(self):
        state = self.ready()
        (self.root / "implementation.py").write_text("value = 2\n")
        self.assert_atomic_failure(lambda: self.fixture.record_verification(state), "inputs changed")

    def test_input_change_after_record_blocks_completion_and_writer(self):
        state = self.recorded()
        (self.root / "implementation.py").write_text("value = 2\n")
        self.assert_atomic_failure(lambda: self.finish(state), "inputs changed")
        state["status"] = "complete"
        self.assert_atomic_failure(lambda: state_module.write_state(self.root, state), "inputs changed")

    def test_missing_existing_input_is_not_implicit_absence(self):
        state = self.recorded()
        (self.root / "implementation.py").unlink()
        self.assert_atomic_failure(lambda: self.finish(state), "cannot safely open")
        with self.assertRaises(state_module.StateError):
            self.capture(files=["implementation.py"])

    def test_explicit_absence_supports_deletion_and_rejects_reappearance(self):
        state = self.ready()
        target = self.root / "implementation.py"
        target.unlink()
        self.set_inputs(self.capture(absent=["implementation.py", "future/missing.py"]))
        state = self.fixture.record_verification(state)
        self.assertEqual(state_module.completion_gate_failures(self.root, state), [])
        target.write_text("reintroduced\n")
        self.assert_atomic_failure(lambda: self.finish(state), "must remain absent")

    def test_absence_change_before_record_is_rejected(self):
        state = self.ready()
        self.set_inputs(self.capture(files=["implementation.py"], absent=["removed.py"]))
        (self.root / "removed.py").write_text("unexpected")
        self.assert_atomic_failure(lambda: self.fixture.record_verification(state), "must remain absent")

    def test_unrelated_file_change_does_not_invalidate_declared_scope(self):
        state = self.recorded()
        (self.root / "unrelated.txt").write_text("outside declared scope")
        self.assertEqual(self.finish(state)["status"], "complete")

    def test_recapture_before_new_checks_allows_new_verification(self):
        state = self.recorded()
        (self.root / "implementation.py").write_text("value = 2\n")
        self.set_inputs(self.capture(files=["implementation.py"]))
        # This focused assertion is the new check, after capture.
        self.assertEqual((self.root / "implementation.py").read_text(), "value = 2\n")
        state = self.fixture.record_verification(state)
        self.assertEqual(self.finish(state)["status"], "complete")

    def test_legacy_record_requires_explicit_revalidation(self):
        state = self.ready()
        self.set_inputs(None)
        self.assert_atomic_failure(lambda: self.fixture.record_verification(state), "lacks pre-check inputs")
        self.fixture.write_verification()
        state = self.fixture.record_verification(state)
        self.set_inputs(None)
        # Simulate a stock 1.4.1 receipt, preserving the legacy digest shape.
        record = state_module.parse_outcome_verification(self.fixture.evidence_path.read_text())
        state["outcome_lock"]["verification"]["semantic_digest"] = state_module.protocol_digest({"record": record, "fidelity_evidence": {}})
        state_module.write_state(self.root, state)
        self.assert_atomic_failure(lambda: self.finish(state), "lacks pre-check inputs")

    def test_justified_manual_outcome_and_empty_scope_rejection(self):
        state = self.ready()
        self.set_inputs(self.capture(manual_reason="Manual protocol inspection only; no file implementation outcome."))
        state = self.fixture.record_verification(state)
        self.assertEqual(self.finish(state)["status"], "complete")
        for kwargs in ({}, {"manual_reason": " "}, {"files": ["implementation.py"], "manual_reason": "mixed"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(state_module.StateError):
                self.capture(**kwargs)

    def test_unsafe_duplicate_and_invalid_inputs_are_rejected(self):
        for path in ("../escape", "/absolute", "a/../b", "a//b", "a\\b", ".littlepowers/state.json", ".git/config", "bad\nname"):
            for kind in ("files", "absent"):
                with self.subTest(path=path, kind=kind), self.assertRaises(state_module.StateError):
                    self.capture(**{kind: [path]})
        with self.assertRaisesRegex(state_module.StateError, "duplicate"):
            self.capture(files=["implementation.py"], absent=["implementation.py"])
        with self.assertRaisesRegex(state_module.StateError, "sha256"):
            state_module.normalize_verification_inputs({"mode": "files", "manual_reason": None, "files": [{"path": "implementation.py", "sha256": "bad"}]})

    def test_self_inclusion_is_rejected(self):
        state = self.ready()
        self.set_inputs(self.capture(files=["docs/evidence/verification.md"]))
        self.assert_atomic_failure(lambda: self.fixture.record_verification(state), "include itself")

    def test_link_and_special_file_inputs_fail_closed(self):
        linked = self.root / "linked.py"
        try:
            linked.symlink_to("implementation.py")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        for kind in ("files", "absent"):
            with self.subTest(kind=kind), self.assertRaises(state_module.StateError):
                self.capture(**{kind: ["linked.py"]})
        linked.unlink()
        linked.symlink_to("missing.py")
        with self.assertRaises(state_module.StateError):
            self.capture(absent=["linked.py"])
        parent = self.root / "linked-parent"
        parent.symlink_to(self.root / "docs", target_is_directory=True)
        with self.assertRaises(state_module.StateError):
            self.capture(absent=["linked-parent/missing.py"])
        for kind in ("files", "absent"):
            with self.subTest(kind=kind), self.assertRaises(state_module.StateError):
                self.capture(**{kind: ["docs"]})
        if hasattr(os, "mkfifo"):
            os.mkfifo(self.root / "pipe")
            with self.assertRaises(state_module.StateError):
                self.capture(files=["pipe"])

    def test_count_and_byte_limits_are_enforced(self):
        with self.assertRaises(state_module.StateError):
            self.capture(absent=[f"missing-{i}" for i in range(state_module.MAX_VERIFICATION_INPUTS + 1)])
        with mock.patch.object(state_module, "MAX_BOUND_FILE_BYTES", 1):
            with self.assertRaisesRegex(state_module.StateError, "exceeds"):
                self.capture(files=["implementation.py"])
        with mock.patch.object(state_module, "MAX_BOUND_TOTAL_BYTES", 1):
            with self.assertRaisesRegex(state_module.StateError, "total bytes"):
                self.capture(files=["implementation.py"])

    def test_cli_capture_is_read_only_and_json_matches_library(self):
        before = state_module.state_path(self.root).read_bytes()
        result = subprocess.run([sys.executable, state_module.__file__, "--root", str(self.root), "verification-inputs", "--file", "implementation.py", "--absent", "deleted.py"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.capture(files=["implementation.py"], absent=["deleted.py"]))
        self.assertEqual(state_module.state_path(self.root).read_bytes(), before)

    def test_direct_file_workflow_rejects_stale_input(self):
        root = self.root / "direct"
        root.mkdir()
        (root / "implementation.py").write_text("value = 1\n")
        state = state_module.command_start(gate_fixture.namespace(
            objective="Set implementation value to one", phase="execute",
            direct_lock=True, next_action="Verify value",
        ), root)
        inputs = state_module.capture_verification_inputs(root, files=["implementation.py"], absent=[])
        self.assertEqual((root / "implementation.py").read_text(), "value = 1\n")
        state = state_module.command_checkpoint(self.fixture.writer(state, phase="verify"), root)
        record = gate_fixture.verification_record()
        record["inputs"] = inputs
        record["outcomes"] = record["outcomes"][:1]
        record["code_quality"] = {"required": False, "status": "not_required", "evidence": []}
        (root / "verification.md").write_text(block("verification", record))
        state = state_module.command_record_verification(self.fixture.writer(state, artifact="verification.md"), root)
        before = state_module.state_path(root).read_bytes()
        (root / "implementation.py").write_text("value = 2\n")
        with self.assertRaisesRegex(state_module.StateError, "inputs changed"):
            state_module.command_finish(self.fixture.writer(state), root, "complete")
        self.assertEqual(state_module.state_path(root).read_bytes(), before)

    def test_absence_permission_error_is_not_absence(self):
        def denied(*args, **kwargs):
            raise state_module.StateError("permission denied") from PermissionError()
        with mock.patch.object(state_module, "_open_workspace_file_descriptor", side_effect=denied):
            with self.assertRaisesRegex(state_module.StateError, "permission denied"):
                self.capture(absent=["missing.py"])

    def test_hardlink_input_is_rejected(self):
        try:
            os.link(self.root / "implementation.py", self.root / "alias.py")
        except (OSError, NotImplementedError):
            self.skipTest("hardlinks unavailable")
        with self.assertRaises(state_module.StateError):
            self.capture(files=["alias.py"])

    def test_absence_requires_an_existing_workspace(self):
        with self.assertRaisesRegex(state_module.StateError, "existing directory"):
            state_module.capture_verification_inputs(
                self.root / "missing-workspace", files=[], absent=["missing.py"],
            )
