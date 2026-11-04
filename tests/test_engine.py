"""evaluation.engine: what each engine runs, against faked processes (no engine needed)."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from evaluation import engine
from evaluation.results import EvaluationError

SHA = "ab" * 32
METADATA = {"id": "demo", "image": "dcp-eval/demo:v1"}


class FakeProcesses:
    """Stands in for run_process: records each command, answers by its first words."""

    def __init__(self, answers=None):
        self.calls, self.answers = [], answers or {}

    def __call__(self, command, timeout, input_bytes=None):
        self.calls.append(command)
        for prefix, answer in self.answers.items():
            if " ".join(command).startswith(prefix):
                return answer.pop(0) if isinstance(answer, list) else answer
        return 0, "", ""

    def find(self, prefix):
        return [call for call in self.calls if " ".join(call).startswith(prefix)]


class Pool(unittest.TestCase):
    """A private core pool and lock folder per test."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {"XDG_RUNTIME_DIR": str(self.root), "DCP_TASKSET": "0-1"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def claim(self, cpus):
        claim = engine.CoreClaim(cpus)
        self.addCleanup(claim.release)
        return claim


class SelectionTests(unittest.TestCase):
    def tearDown(self):
        engine.current.cache_clear()

    def test_dcp_engine_picks_the_engine(self):
        for name, kind in (("docker", engine.Docker), ("podman", engine.Podman), ("apptainer", engine.Apptainer)):
            engine.current.cache_clear()
            with patch.dict(os.environ, {"DCP_ENGINE": name}):
                self.assertIs(type(engine.current()), kind)

    def test_unknown_engine_is_an_infrastructure_error(self):
        with patch.dict(os.environ, {"DCP_ENGINE": "lxc"}), self.assertRaises(EvaluationError) as caught:
            engine.current()
        self.assertEqual(caught.exception.reason, "infrastructure_error")


@unittest.skipUnless(sys.platform.startswith("linux"), "core claims use Linux affinity and flock")
class CoreClaimTests(Pool):
    def test_concurrent_claims_get_distinct_cores_until_the_pool_is_empty(self):
        first, second = self.claim(1), self.claim(1)
        self.assertEqual((first.cores, second.cores), ([0], [1]))
        with self.assertRaises(EvaluationError) as caught:
            self.claim(1)
        self.assertEqual(caught.exception.reason, "infrastructure_error")
        first.release()
        self.assertEqual(self.claim(1).cores, [0])

    def test_fractional_cpus_get_whole_cores(self):
        os.environ["DCP_TASKSET"] = "0-3,8"
        self.assertEqual(self.claim(2.5).text, "0,1,2")
        self.assertEqual(engine.parse_cpu_list("0-3,8"), [0, 1, 2, 3, 8])


class DockerTests(unittest.TestCase):
    def test_run_isolates_and_limits_and_removes(self):
        fake = FakeProcesses({"docker inspect": (0, "false\n", "")})
        with patch.object(engine, "run_process", fake):
            run = engine.Docker().run(METADATA, "sha256:" + SHA, Path("/stage"), memory_mb=256, cpus=1, timeout=9)
        command = fake.calls[0]
        for flag in ("--network=none", "--read-only", "--user=65534:65534", "--cap-drop=ALL", "--pids-limit=128"):
            self.assertIn(flag, command)
        self.assertEqual(command[command.index("--cpus") + 1], "1")
        self.assertEqual(command[-1], "sha256:" + SHA)  # the identity, not the tag
        self.assertFalse(run.oom_killed)
        self.assertTrue(fake.find("docker rm --force dcp-eval-"))

    def test_cleanup_accepts_podman_wording(self):
        fake = FakeProcesses({"podman rm": (1, "", 'Error: no container with name or ID "x" found: no such container')})
        with patch.object(engine, "run_process", fake):
            engine.Podman().remove("x")  # does not raise


@unittest.skipUnless(sys.platform.startswith("linux"), "core claims use Linux affinity and flock")
class PodmanTests(Pool):
    def run_podman(self, controllers):
        seccomp = self.root / "seccomp.json"
        seccomp.write_text('{"syscalls": [{"names": ["read", "sched_setaffinity"], "action": "SCMP_ACT_ALLOW"}]}')
        fake = FakeProcesses({"podman inspect": (0, "false\n", ""), "taskset": (0, "", "")})
        with patch.object(engine, "run_process", fake), patch.object(engine, "CACHE", self.root / "cache"), \
                patch.object(engine, "delegated_controllers", return_value=controllers), \
                patch.dict(os.environ, {"DCP_SECCOMP_DEFAULT": str(seccomp)}):
            engine.Podman().run(METADATA, SHA, Path("/stage"), memory_mb=256, cpus=1, timeout=9)
        return fake.calls[0]

    def test_without_cpu_controller_a_run_gets_its_own_core_and_cannot_widen_it(self):
        command = self.run_podman({"memory", "pids"})
        self.assertEqual(command[:3], ["taskset", "-c", "0"])
        self.assertIn("--user=0:0", command)
        self.assertNotIn("--cpus", command)
        profile = next(arg.split("=", 2)[2] for arg in command if arg.startswith("--security-opt=seccomp="))
        self.assertIn('"names": ["sched_setaffinity"], "action": "SCMP_ACT_ERRNO"', Path(profile).read_text())
        self.assertEqual(self.claim(1).cores, [0])  # released after the run

    def test_with_cpu_controller_cpus_pass_through(self):
        command = self.run_podman({"cpu", "memory", "pids"})
        self.assertEqual(command[0], "podman")
        self.assertEqual(command[command.index("--cpus") + 1], "1")
        self.assertFalse(any(arg.startswith("--security-opt=seccomp=") for arg in command))

    def test_build_rewrites_add_checksum_and_mounts_helpers(self):
        folder = self.root / "solvers" / "demo"
        folder.mkdir(parents=True)
        (folder / "Dockerfile").write_text(f"FROM x\nADD --checksum=sha256:{SHA} https://e.org/a.tgz /a.tgz\n")
        (self.root / "cache").mkdir()
        (self.root / "cache" / "nochown.so").write_text("")
        seen = []

        def fake_run(command, **kwargs):
            if command[:2] == ["podman", "build"]:
                dockerfile = command[command.index("-f") + 1]
                seen.append((command, Path(dockerfile).read_text()))
            return type("Done", (), {"stdout": "", "returncode": 0})()

        with patch.object(engine, "CACHE", self.root / "cache"), patch.object(engine, "integration_folder",
                                                                             return_value=folder), \
                patch.object(engine.subprocess, "run", fake_run):
            engine.Podman().build("demo", METADATA, "sha256:recipe")
        [(command, dockerfile)] = seen
        self.assertTrue(any(arg.endswith(":/etc/ld.so.preload:ro") for arg in command))
        self.assertIn(f"RUN echo '{SHA}  /a.tgz' | sha256sum -c -", dockerfile)
        self.assertIn("org.dcp-rosetta.recipe=sha256:recipe", command)


@unittest.skipUnless(sys.platform.startswith("linux"), "core claims use Linux affinity and flock")
class ApptainerTests(Pool):
    def setUp(self):
        super().setUp()
        (self.root / "images").mkdir()
        (self.root / "images" / "demo.sif").write_bytes(b"sif")
        self.images = patch.dict(os.environ, {"DCP_APPTAINER_IMAGES": str(self.root / "images")})
        self.images.start()

    def tearDown(self):
        self.images.stop()
        super().tearDown()

    def run_apptainer(self, controllers, answers):
        fake = FakeProcesses(answers)
        with patch.object(engine, "run_process", fake), \
                patch.object(engine, "delegated_controllers", return_value=controllers):
            run = engine.Apptainer().run(METADATA, "sha256:x", Path("/stage"), memory_mb=256, cpus=1, timeout=9)
        return run, fake

    def test_run_is_a_bounded_systemd_unit_on_its_own_core(self):
        run, fake = self.run_apptainer({"memory", "pids"}, {"systemd-run": (0, "{}\n", ""),
                                                            "systemctl --user show": (0, "Result=success\nLoadState=not-found\n", "")})
        command = fake.calls[0]
        self.assertEqual(command[:3], ["systemd-run", "--user", "--quiet"])
        properties = [command[i + 1] for i, word in enumerate(command) if word == "-p"]
        self.assertEqual(properties, ["MemoryMax=256M", "MemorySwapMax=0", "TasksMax=160", "CPUAffinity=0",
                                      "SystemCallFilter=~sched_setaffinity", "SystemCallErrorNumber=EPERM"])
        self.assertIn("--containall", command)
        self.assertEqual(command[command.index("--network") + 1], "none")
        self.assertIn("/stage:/input:ro", command)
        self.assertEqual(command[-1], str(self.root / "images" / "demo.sif"))
        self.assertEqual(command[command.index("--containall") - 1], "run")
        self.assertEqual((run.code, run.stdout, run.oom_killed), (0, "{}\n", False))
        self.assertTrue(fake.find("systemctl --user stop dcp-eval-"))
        self.assertEqual(self.claim(1).cores, [0])  # released after the run

    def test_cpu_controller_gives_a_quota(self):
        _, fake = self.run_apptainer({"cpu", "memory", "pids"}, {"systemctl --user show": (0, "Result=success\n", "")})
        properties = [fake.calls[0][i + 1] for i, word in enumerate(fake.calls[0]) if word == "-p"]
        self.assertIn("CPUQuota=100%", properties)
        self.assertFalse(any(p.startswith("CPUAffinity") for p in properties))

    def test_oom_kill_is_read_from_the_unit(self):
        run, _ = self.run_apptainer({"memory", "pids"}, {
            "systemd-run": (1, "", ""),
            "systemctl --user show": [(0, "Result=oom-kill\nLoadState=loaded\n", ""),
                                      (0, "Result=success\nLoadState=not-found\n", "")]})
        self.assertTrue(run.oom_killed)

    def test_systemd_run_failing_is_an_infrastructure_error(self):
        with self.assertRaises(EvaluationError) as caught:
            self.run_apptainer({"memory", "pids"}, {
                "systemd-run": (1, "", "Failed to connect to bus"),
                "systemctl --user show": (0, "Result=success\nLoadState=not-found\n", "")})
        self.assertEqual(caught.exception.reason, "infrastructure_error")
        self.assertIn("Failed to connect to bus", caught.exception.detail)

    def test_identity_is_the_sif_digest(self):
        import hashlib
        self.assertEqual(engine.Apptainer().image_identity(METADATA), "sha256:" + hashlib.sha256(b"sif").hexdigest())

    def test_missing_sif_is_an_infrastructure_error(self):
        with self.assertRaises(EvaluationError) as caught:
            engine.Apptainer().image_identity({"id": "absent", "image": "x"})
        self.assertEqual(caught.exception.reason, "infrastructure_error")


class RewriteTests(unittest.TestCase):
    def test_checksum_becomes_a_sha256sum_check(self):
        self.assertEqual(engine.rewrite_add_checksum(f"FROM x\nADD --checksum=sha256:{SHA} https://e.org/a.tgz /opt/a.tgz\n"
                                                     "RUN ls\n"),
                         f"FROM x\nADD https://e.org/a.tgz /opt/a.tgz\nRUN echo '{SHA}  /opt/a.tgz' | sha256sum -c -\n"
                         "RUN ls\n")

    def test_continued_line(self):
        self.assertEqual(engine.rewrite_add_checksum(f"ADD --checksum=sha256:{SHA} \\\n    https://e.org/a.tgz \\\n"
                                                     "    /a.tgz\n"),
                         f"ADD https://e.org/a.tgz /a.tgz\nRUN echo '{SHA}  /a.tgz' | sha256sum -c -\n")

    def test_other_lines_unchanged(self):
        text = "FROM x\nADD https://e.org/a.tgz /a.tgz\nCOPY --chmod=755 a /a\n"
        self.assertEqual(engine.rewrite_add_checksum(text), text)

    def test_seccomp_profile_denies_only_setaffinity(self):
        profile = engine.without_setaffinity({"syscalls": [
            {"names": ["read", "sched_setaffinity"], "action": "SCMP_ACT_ALLOW"},
            {"names": ["sched_setaffinity"], "action": "SCMP_ACT_ALLOW", "includes": {"caps": ["CAP_SYS_NICE"]}}]})
        self.assertEqual(profile["syscalls"], [{"names": ["read"], "action": "SCMP_ACT_ALLOW"},
                                               {"names": ["sched_setaffinity"], "action": "SCMP_ACT_ERRNO",
                                                "errnoRet": 1}])


if __name__ == "__main__":
    unittest.main()
