"""tools/podman: the docker stand-in's argument mapping and CPU limits, against a fake podman."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools" / "podman" / "docker"
REWRITE = ROOT / "tools" / "podman" / "rewrite_dockerfile.py"
SHA = "ab" * 32

# Logs its arguments one per line, then the cores taskset gave it, then sleeps if asked.
FAKE_PODMAN = """#!/bin/bash
if [ "$1" = info ]; then echo "$FAKE_LOGS"; exit 0; fi
log="$FAKE_LOGS/$(date +%s%N).log"
printf '%s\\n' "$@" > "$log.tmp"; echo "cores=${FAKE_CORES:-none}" >> "$log.tmp"; mv "$log.tmp" "$log"
sleep "${FAKE_SLEEP:-0}"
"""
FAKE_TASKSET = """#!/bin/bash
if [ "$1" = -pc ]; then echo "pid $2's current affinity list: 0-3"; exit 0; fi
[ "$1" = -c ] || exit 9
export FAKE_CORES=$2; shift 2; exec "$@"
"""
RUN = ["run", "--pull=never", "--name", "dcp-eval-x", "--user=65534:65534", "--cpus", "1", "image:tag"]


@unittest.skipUnless(sys.platform.startswith("linux"), "the wrapper is a Linux bash script")
class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bin, self.logs = self.root / "bin", self.root / "logs"
        self.bin.mkdir(); self.logs.mkdir()
        for name, text in (("podman", FAKE_PODMAN), ("taskset", FAKE_TASKSET)):
            (self.bin / name).write_text(text); (self.bin / name).chmod(0o755)
        self.controllers = self.root / "cgroup.controllers"
        self.controllers.write_text("memory pids\n")
        self.seccomp = self.root / "seccomp.json"
        self.seccomp.write_text(json.dumps({"defaultAction": "SCMP_ACT_ERRNO", "syscalls": [
            {"names": ["read", "sched_setaffinity"], "action": "SCMP_ACT_ALLOW"},
            {"names": ["sched_setaffinity"], "action": "SCMP_ACT_ALLOW", "includes": {"caps": ["CAP_SYS_NICE"]}}]}))
        self.env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_LOGS": str(self.logs),
                    "XDG_CACHE_HOME": str(self.root / "cache"), "XDG_RUNTIME_DIR": str(self.root / "runtime"),
                    "DCP_CGROUP_CONTROLLERS": str(self.controllers), "DCP_SECCOMP_DEFAULT": str(self.seccomp),
                    "DCP_TASKSET": "0-1"}

    def tearDown(self):
        self.temp.cleanup()

    def docker(self, *args, **env):
        return subprocess.run([str(WRAPPER), *args], env={**self.env, **env}, capture_output=True, text=True)

    def calls(self):
        return [path.read_text().splitlines() for path in sorted(self.logs.glob("*.log"))]

    def test_run_maps_user_and_pins_one_core_without_cpu_controller(self):
        self.assertEqual(self.docker(*RUN).returncode, 0)
        [call] = self.calls()
        self.assertIn("--user=0:0", call)
        self.assertNotIn("--cpus", " ".join(call))
        self.assertEqual(call[-1], "cores=0")
        profile = next(arg.split("=", 2)[2] for arg in call if arg.startswith("--security-opt=seccomp="))
        rules = json.loads(Path(profile).read_text())["syscalls"]
        allowed = [name for rule in rules if rule["action"] == "SCMP_ACT_ALLOW" for name in rule["names"]]
        self.assertEqual(allowed, ["read"])
        self.assertIn({"names": ["sched_setaffinity"], "action": "SCMP_ACT_ERRNO", "errnoRet": 1}, rules)
        self.assertEqual(self.docker("dcp-cpu-limit").stdout.strip(), "cores")

    def test_fractional_cpus_get_whole_cores(self):
        self.env["DCP_TASKSET"] = "0-3"
        self.assertEqual(self.docker(*RUN[:-3], "--cpus=2.5", "image:tag").returncode, 0)
        self.assertEqual(self.calls()[0][-1], "cores=0,1,2")

    def test_concurrent_runs_get_distinct_cores_until_the_pool_is_empty(self):
        running = []
        try:
            for count in (1, 2):
                running.append(subprocess.Popen([str(WRAPPER), *RUN], env={**self.env, "FAKE_SLEEP": "3"}))
                deadline = time.time() + 10
                while len(self.calls()) < count and time.time() < deadline:
                    time.sleep(0.05)
            full = self.docker(*RUN)
            self.assertEqual(full.returncode, 125)
            self.assertIn("dcp-podman: infrastructure: no 1 free core(s) in pool 0-1", full.stderr)
        finally:
            for process in running:
                self.assertEqual(process.wait(), 0)
        self.assertEqual(sorted(call[-1] for call in self.calls()), ["cores=0", "cores=1"])
        self.assertEqual(self.docker(*RUN).returncode, 0)  # the first run's core is free again

    def test_pool_defaults_to_this_process_affinity(self):
        del self.env["DCP_TASKSET"]
        self.assertEqual(self.docker(*RUN).returncode, 0)
        self.assertEqual(self.calls()[0][-1], "cores=0")

    def test_cpus_pass_through_with_cpu_controller(self):
        self.controllers.write_text("cpuset cpu io memory pids\n")
        self.assertEqual(self.docker(*RUN).returncode, 0)
        [call] = self.calls()
        self.assertEqual(call[:2], ["run", "--cpus=1"])
        self.assertIn("--user=0:0", call)
        self.assertFalse(any(arg.startswith("--security-opt=seccomp=") for arg in call))
        self.assertEqual(call[-1], "cores=none")
        self.assertEqual(self.docker("dcp-cpu-limit").stdout.strip(), "quota")

    def test_other_commands_pass_through(self):
        self.assertEqual(self.docker("rm", "--force", "dcp-eval-x").returncode, 0)
        self.assertEqual(self.calls()[0], ["rm", "--force", "dcp-eval-x", "cores=0-1"])

    def test_build_rewrites_add_checksum_and_mounts_helpers(self):
        (self.root / "cache" / "dcp-podman").mkdir(parents=True)
        (self.root / "cache" / "dcp-podman" / "nochown.so").write_text("")  # skips the gcc step
        dockerfile = self.root / "Dockerfile"
        dockerfile.write_text(f"FROM x\nADD --checksum=sha256:{SHA} https://e.org/a.tgz /a.tgz\n")
        self.assertEqual(self.docker("build", "-t", "t", "-f", str(dockerfile), ".", DCP_TASKSET="").returncode, 0)
        [call] = self.calls()
        self.assertIn("-v", call)
        self.assertTrue(any(arg.endswith(":/etc/ld.so.preload:ro") for arg in call))
        self.assertNotEqual(call[call.index("-f") + 1], str(dockerfile))
        self.assertFalse(Path(call[call.index("-f") + 1]).exists())  # the rewritten copy is removed


class RewriteTests(unittest.TestCase):
    def rewrite(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".Dockerfile", delete=False) as handle:
            handle.write(text)
        try:
            return subprocess.run([sys.executable, str(REWRITE), handle.name],
                                  capture_output=True, text=True, check=True).stdout
        finally:
            os.unlink(handle.name)

    def test_checksum_becomes_a_sha256sum_check(self):
        self.assertEqual(self.rewrite(f"FROM x\nADD --checksum=sha256:{SHA} https://e.org/a.tgz /opt/a.tgz\nRUN ls\n"),
                         f"FROM x\nADD https://e.org/a.tgz /opt/a.tgz\n"
                         f"RUN echo '{SHA}  /opt/a.tgz' | sha256sum -c -\nRUN ls\n")

    def test_continued_line(self):
        self.assertEqual(self.rewrite(f"ADD --checksum=sha256:{SHA} \\\n    https://e.org/a.tgz \\\n    /a.tgz\n"),
                         f"ADD https://e.org/a.tgz /a.tgz\nRUN echo '{SHA}  /a.tgz' | sha256sum -c -\n")

    def test_other_lines_unchanged(self):
        text = "FROM x\nADD https://e.org/a.tgz /a.tgz\nCOPY --chmod=755 a /a\n"
        self.assertEqual(self.rewrite(text), text)


if __name__ == "__main__":
    unittest.main()
