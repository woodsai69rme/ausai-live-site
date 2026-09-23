#!/usr/bin/env python3
# ============================================
# Unit tests for war_room.cmd_validate_tools 9-state machine
# Uses unittest.mock to simulate all 9 combinations WITHOUT
# executing real java/apktool/jadx.
#
# 9 states = 3 tools x {FOUND, NOT_FOUND, BROKEN}.
# 4 tests below cover the most representative combinations:
#   1. all_NOT_FOUND          -> aggregate:OK
#   2. java_FOUND_others_NF   -> aggregate:OK
#   3. java_BROKEN_others_NF  -> aggregate:FAIL
#   4. JSON output shape      -> shape + numeric exit codes preserved
#
# Run with:  python -m pytest tests/unit/test_war_room_validate_tools.py -v
# ============================================
"""
Mocked-subprocess tests for war_room.cmd_validate_tools.

Why mocks:
- The function calls `java.exe -version` and `<tool>.bat --version` via subprocess.run
- Real subprocess invocations aren't deterministic on CI (depends on operator's
  actual jar/bat layout, antimalware, etc.)
- Mocks let us test the 9-state logic without depending on real tool installs.

Coverage of cmd_validate_tools 9-state machine is in TestValidateTools9State below.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


JAVA_FOUND_STDERR = 'openjdk version "17.0.10" 2024-01-16\nOpenJDK 64-Bit Server VM (build 17.0.10+7, mixed mode)\n'
APKTOOL_FOUND_STDOUT = "2.9.3\n"
JADX_FOUND_STDOUT = "1.5.0\n"


def _bi_side_effect(table: dict):
    """Build an os.path.exists side_effect function from a set of substrings
    that, when present in the path, return True; otherwise False."""
    substrings_true = list(table.keys())

    def _impl(p: str) -> bool:
        for s in substrings_true:
            if s in p:
                return table[s]
        return False

    return _impl


class TestValidateTools9State(unittest.TestCase):
    """9-state machine test via unittest.mock on subprocess.run + os.path.exists + shutil.which."""

    @classmethod
    def setUpClass(cls) -> None:
        # Lazy import: war_room's auto-extend reads MOBILE_FILTERED.csv on import,
        # which is harmless but slow. Do it once per class.
        import war_room  # noqa: F401
        cls.war_room = war_room

    def setUp(self) -> None:
        self.cmd = self.war_room.cmd_validate_tools
        # Default user has no java, no portable JDK, no .bat files
        self._env_baseline = {
            "USERPROFILE": "C:\\Users\\karma",
            "PATHEXT": ".EXE;.BAT;.CMD",
            "PATH": "C:\\Windows\\System32",
            "JAVA_HOME": "",
        }
        # Args object: argparse.Namespace (more accurate than mock.Mock)
        self.args = argparse.Namespace(json=False, verbose=False)

    # -- Test 1: all tools NOT_FOUND --------------------------------
    def test_all_not_found_returns_zero(self) -> None:
        # No JAVA_HOME, no portable JDK, java not on PATH, .bat files don't exist
        # Result: java/apktool/jadx all [INFO] (NOT_FOUND). Aggregate OK -> rc=0.
        env = {**self._env_baseline}
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch("os.path.exists", return_value=False), \
             mock.patch("os.name", "nt"), \
             mock.patch("shutil.which", return_value=None):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = self.cmd(self.args)
            self.assertEqual(rc, 0, "all NOT_FOUND -> aggregate OK expected rc=0")
            out = buf.getvalue()
            self.assertIn("java", out)
            self.assertIn("apktool", out)
            self.assertIn("jadx", out)
            self.assertIn("INFO", out)

    # -- Test 2: java FOUND, others NOT_FOUND -----------------------
    def test_java_found_aggregate_ok(self) -> None:
        # JAVA_HOME defined; os.path.exists returns True only for JAVA_HOME\bin\java.exe.
        # subprocess.run mocked to return openjdk version on rc=0.
        # .bat files NOT present -> apktool/jadx NOT_FOUND.
        env = {**self._env_baseline, "JAVA_HOME": "C:\\Program Files\\Java\\jdk-17"}
        exists_table = {
            "Program Files\\Java\\jdk-17\\bin\\java.exe": True,
        }
        cp_java = mock.Mock(returncode=0, stdout="", stderr=JAVA_FOUND_STDERR)
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch("os.path.exists", side_effect=_bi_side_effect(exists_table)), \
             mock.patch("os.name", "nt"), \
             mock.patch("shutil.which", return_value=None), \
             mock.patch("subprocess.run", return_value=cp_java) as run_mock:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = self.cmd(self.args)
            self.assertEqual(rc, 0, "java FOUND + others NOT_FOUND -> aggregate OK rc=0 expected")
            # subprocess.run was called once (for java -version); apktool/jadx NOT executables
            self.assertEqual(run_mock.call_count, 1)
            # First arg of first call is the java executable path.
            # call_args_list[0] = call(...); [0] = tuple-of-args; [0][0] = [java_exe, "-version"];
            # [0][0][0] = java_exe (string). We substring-check for "java.exe".
            first_cmd_argv = run_mock.call_args_list[0][0][0][0]
            self.assertTrue(first_cmd_argv.endswith("java.exe"),
                            msg=f"first subprocess.run argv should end in java.exe, got: {first_cmd_argv!r}")

    # -- Test 3: java BROKEN, others NOT_FOUND -------------------
    # Aggregate must be FAIL because real BROKEN is a problem state.
    def test_java_broken_aggregate_fail(self) -> None:
        env = {**self._env_baseline, "JAVA_HOME": "C:\\Program Files\\Java\\jdk-17"}
        exists_table = {
            "Program Files\\Java\\jdk-17\\bin\\java.exe": True,
        }
        cp_java_broken = mock.Mock(returncode=1, stdout="", stderr="Segmentation fault\n")
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch("os.path.exists", side_effect=_bi_side_effect(exists_table)), \
             mock.patch("os.name", "nt"), \
             mock.patch("shutil.which", return_value=None), \
             mock.patch("subprocess.run", return_value=cp_java_broken):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = self.cmd(self.args)
            self.assertEqual(rc, 1, "java BROKEN -> aggregate FAIL rc=1 expected")
            out = buf.getvalue()
            self.assertIn("BROKEN", out)
            self.assertIn("java", out)

    # -- Test 4: --json output shape ------------------------------
    def test_apktool_found_via_manifest_mf(self) -> None:
        """Verify that apktool/jadx versions are read from META-INF/MANIFEST.MF
        (Implementation-Version) directly via zipfile -- NO subprocess,
        NO JVM cold-start, NO 30s+ hang on (apktool jars don't support --version)."""
        import tempfile as _tempfile
        import zipfile as _zipfile
        with _tempfile.TemporaryDirectory() as tmpdir:
            # Set up a fake Tools\apktool\ with a fake .jar containing MANIFEST.MF
            env = {**self._env_baseline, "USERPROFILE": tmpdir}
            fake_apktool_dir = os.path.join(tmpdir, "Tools", "apktool")
            os.makedirs(fake_apktool_dir, exist_ok=True)
            fake_jar = os.path.join(fake_apktool_dir, "apktool_2.9.3.jar")
            with _zipfile.ZipFile(fake_jar, "w") as zf:
                zf.writestr("META-INF/MANIFEST.MF",
                            b"Manifest-Version: 1.0\r\nImplementation-Version: 2.9.3\r\n")
            # JAVA_HOME set so java also looks FOUND; mock subprocess.run for java
            env["JAVA_HOME"] = os.path.join(tmpdir, "fake-java")
            cp_java = mock.Mock(returncode=0, stdout="", stderr=JAVA_FOUND_STDERR)
            # Create Tools\jadx\lib\ dir too (empty) so real os.listdir / os.path.isdir
            # work without false-positive mocking.
            os.makedirs(os.path.join(tmpdir, "Tools", "jadx", "lib"), exist_ok=True)
            # os.path.exists needs to return True for the JAVA_HOME\bin\java.exe path
            # for cmd_validate_tools' JAVA_HOME branch to fire. Use substring match.
            def _exists(p):
                return ("fake-java\\bin\\java.exe" in p) or ("jdk-17\\bin\\java.exe" in p)
            with mock.patch.dict(os.environ, env, clear=False), \
                 mock.patch("os.path.exists", side_effect=_exists), \
                 mock.patch("os.name", "nt"), \
                 mock.patch("shutil.which", return_value=None), \
                 mock.patch("subprocess.run", return_value=cp_java) as run_mock:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = self.cmd(self.args)
                out = buf.getvalue()
                self.assertEqual(rc, 0,
                                 msg=f"apktool should be FOUND via Manifest.MF, got rc={rc} | output:\n{out}")
                self.assertIn("2.9.3", out, msg=f"output should show apktool version 2.9.3 | output:\n{out}")
                # Crucial: subprocess.run was called ONCE (only for java -version).
                # It was NOT called for apktool --version (the slow path we dropped).
                self.assertEqual(run_mock.call_count, 1,
                                 msg="subprocess.run should only be called once (for java -version), not for apktool --version")
                self.assertIn("java.exe", run_mock.call_args_list[0][0][0][0])

    def test_json_output_shape(self) -> None:
        env = {**self._env_baseline}
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch("os.path.exists", return_value=False), \
             mock.patch("os.name", "nt"), \
             mock.patch("shutil.which", return_value=None):
            args_json = argparse.Namespace(json=True, verbose=False)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = self.cmd(args_json)
            self.assertEqual(rc, 0)
            # Parse the captured stdout as JSON
            data = json.loads(buf.getvalue())
            self.assertIn("aggregate_ok", data)
            self.assertIn("tools", data)
            self.assertIn("remediation", data)
            self.assertIsInstance(data["tools"], dict)
            self.assertEqual(set(data["tools"].keys()), {"java", "apktool", "jadx"})
            for tool_name, entry in data["tools"].items():
                self.assertIn("status", entry)
                self.assertIn("version", entry)
                self.assertIn("path", entry)
                self.assertEqual(entry["status"], "NOT_FOUND")
            self.assertIsInstance(data["remediation"], list)
            self.assertGreater(len(data["remediation"]), 0,
                               msg="remediation list should have at least 1 hint (run install_jdk_portable.ps1)")


if __name__ == "__main__":
    unittest.main()
