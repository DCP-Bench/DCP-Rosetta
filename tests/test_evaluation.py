from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from bench.dcp_bench.reference import ReferenceSession
from evaluation.check import evaluate
from evaluation.execution import OOM_REREADS, _copied_sources, execute, recipe, validate_records
from evaluation.legacy import solver_id
from evaluation.results import EvaluationError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''


def built_image():
    """Stand in for the cpmpy_python image, which CI builds only after these tests run."""
    return patch.multiple("evaluation.check", image_identity=lambda metadata: "sha256:test",
                          image_recipe=lambda metadata: "sha256:recipe")


class OrchestrationTests(unittest.TestCase):
    def run_records(self, records, timing=None, **kwargs):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_text("# deliberately not executable on host")
            with built_image(), patch("evaluation.check.execute", return_value=(records, timing or {})):
                return evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE, instances=[], **kwargs)

    def test_runner_records_are_validated(self):
        for records in ([], [{}], [{"type": "status", "status": "success"}],
                        [{"type": "status", "status": "limit"}, {"type": "solution", "values": {}}]):
            with self.assertRaises(EvaluationError): validate_records(records)

    def test_solution_count_is_bounded(self):
        """Duplicate records must not each cost a reference solve."""
        one = {"type": "solution", "values": {"x": 0, "y": 2}}
        status = {"type": "status", "status": "complete"}
        checks = []
        real = ReferenceSession.check
        with patch.object(ReferenceSession, "check", lambda s, v: checks.append(v) or real(s, v)):
            result = self.run_records([one] * 50 + [status], solution_limit=2)
        self.assertEqual(result["reason"], "invalid_output")
        self.assertEqual(checks, [])
        checks.clear()
        with patch.object(ReferenceSession, "check", lambda s, v: checks.append(v) or real(s, v)):
            self.assertTrue(self.run_records([one, one, status], solution_limit=2)["accepted"])
        self.assertEqual(len(checks), 2)

    def test_exhaustion_and_duplicates(self):
        one = {"type": "solution", "values": {"x": 0, "y": 2}}
        for status, accepted, reason in (("limit", False, "invalid_output"), ("complete", True, "accepted"),
                                         ("timeout", False, "execution_timeout")):
            result = self.run_records([one, one, {"type": "status", "status": status}], solution_limit=2)
            self.assertEqual((result["accepted"], result["reason"]), (accepted, reason), result)
        self.assertFalse(self.run_records([{"type": "status", "status": "complete"}])["accepted"])

    def test_tolerating_inconclusive_instances(self):
        """Skipping a timeout relaxes coverage; it must never relax soundness."""
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        bad = {"type": "solution", "values": {"x": 0, "y": 0}}
        stop = {"type": "status", "status": "limit"}
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_text("# stub")
            second = [{"n": 3, "optimize": False}]

            def run(records, **kwargs):
                with built_image(), patch("evaluation.check.execute", side_effect=records):
                    return evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE,
                                    instances=second, instance_count=2, **kwargs)

            # The first instance times out in the container, the second is fine.
            timeout = [{"type": "status", "status": "timeout"}]
            records = [(timeout, {}), ([{"type": "solution", "values": {"x": 0, "y": 3}}, stop], {})]
            strict = run(list(records))
            self.assertEqual((strict["accepted"], strict["reason"]), (False, "execution_timeout"))
            self.assertEqual(strict["skipped_instances"], [])

            lenient = run(list(records), tolerate_inconclusive=True)
            self.assertTrue(lenient["accepted"], lenient)
            self.assertEqual(lenient["skipped_instances"], ["example"])
            self.assertEqual(lenient["instances_checked"], 1)
            self.assertTrue(lenient["instances"][0]["skipped"])
            self.assertEqual(lenient["requested"]["tolerate_inconclusive"], True)

            # A rejected solution still fails, tolerated or not.
            counterexample = [([bad, stop], {}), ([good, stop], {})]
            for tolerate in (False, True):
                with self.subTest(tolerate=tolerate):
                    result = run(list(counterexample), tolerate_inconclusive=tolerate)
                    self.assertEqual(result["reason"], "invalid_solution", result)

            # Running out of memory is skipped the same way.
            memory = [([{"type": "status", "status": "error"}], {"oom_killed": True}),
                      ([{"type": "solution", "values": {"x": 0, "y": 3}}, stop], {})]
            lenient = run(list(memory), tolerate_inconclusive=True)
            self.assertTrue(lenient["accepted"], lenient)
            self.assertEqual(lenient["instances"][0]["reason"], "memory_limit")

            # Nothing verified at all cannot pass.
            nothing = [(timeout, {}), (timeout, {})]
            empty = run(list(nothing), tolerate_inconclusive=True)
            self.assertEqual((empty["accepted"], empty["reason"]), (False, "no_instance_verified"))
            self.assertEqual(len(empty["skipped_instances"]), 2)

    def test_reference_and_instance_errors(self):
        self.assertEqual(self.run_records([], instance_count=0)["reason"], "invalid_request")
        self.assertEqual(self.run_records([], instance_ids=["json:0"])["reason"], "invalid_request")
        self.assertEqual(self.run_records([], execution_timeout=-1)["reason"], "invalid_request")

    def test_instance_budget_is_not_a_requirement(self):
        """Asking for more instances than exist checks every one that exists."""
        records = [{"type": "solution", "values": {"x": 0, "y": 2}}, {"type": "status", "status": "limit"}]
        result = self.run_records(records, instance_count=7)
        self.assertTrue(result["accepted"], result)
        self.assertEqual((result["instances_available"], result["instances_checked"]), (1, 1))
        self.assertEqual(result["requested"]["instance_count"], 7)

    def test_counterexample_survives_a_bad_ending(self):
        """A rejected solution disproves the model however the run ended."""
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        bad = {"type": "solution", "values": {"x": 0, "y": 0}}
        for ending in ("timeout", "error", "limit", "complete"):
            with self.subTest(ending=ending):
                result = self.run_records([good, bad, {"type": "status", "status": ending}], solution_limit=5)
                self.assertEqual(result["reason"], "invalid_solution", result)
                self.assertEqual(result["instances"][0]["solutions_checked"], 1)

    def test_clean_solutions_then_a_bad_ending_are_inconclusive(self):
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        for ending, reason in (("timeout", "execution_timeout"), ("error", "execution_error")):
            with self.subTest(ending=ending):
                result = self.run_records([good, {"type": "status", "status": ending}], solution_limit=5)
                self.assertEqual(result["reason"], reason, result)
                # The verified work is still reported, so a consumer can weigh it.
                self.assertEqual(result["instances"][0]["solutions_checked"], 1)

    def test_a_run_that_fails_after_an_oom_kill_is_a_memory_limit(self):
        """A runner that outlived its killed solver reports an error; the kill decides the reason."""
        good = {"type": "solution", "values": {"x": 0, "y": 2}}
        error = {"type": "status", "status": "error", "detail": "the solver reported an error"}
        for records, oom_killed, reason in (([error], True, "memory_limit"), ([error], False, "execution_error"),
                                            ([{"type": "status", "status": "unsat"}], True, "memory_limit"),
                                            ([good, error], True, "memory_limit"),
                                            # Answers the runner still gave in full stand.
                                            ([good, {"type": "status", "status": "limit"}], True, "accepted")):
            with self.subTest(records=records, oom_killed=oom_killed):
                result = self.run_records(records, timing={"oom_killed": oom_killed})
                self.assertEqual(result["reason"], reason, result)
        bad = {"type": "solution", "values": {"x": 0, "y": 0}}
        result = self.run_records([bad, error], timing={"oom_killed": True})
        self.assertEqual(result["reason"], "invalid_solution", result)

    def test_exit_137_is_a_memory_limit_only_when_docker_saw_an_oom_kill(self):
        """A submission can SIGKILL itself; only the kernel's kill counts as the memory limit.

        Docker can set OOMKilled after the exit, so an unset flag after an exit
        137 is read again, and the detail gives the reading at exit and the last one.
        """
        rereads = OOM_REREADS
        for flags, reason, inspections, readings in (
                (["true"], "memory_limit", 1, "OOMKilled was true at exit"),
                (["false", "false", "true"], "memory_limit", 3, "OOMKilled was false at exit and true 0.5 s later"),
                (["false"] * (rereads + 1), "execution_error", rereads + 1,
                 f"OOMKilled was false at exit and false {rereads * 0.25:g} s later")):
            commands = []
            answers = iter(flags)

            def docker(command, timeout):
                commands.append(command[1])
                if command[1] == "inspect":
                    return 0, next(answers) + "\n", ""
                return {"run": (137, "", "Killed"), "rm": (0, "", "")}[command[1]]

            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as temp, \
                    patch("evaluation.execution.run_process", side_effect=docker), \
                    patch("evaluation.execution.time.sleep"):
                model = Path(temp) / "model.py"
                model.write_text("# stub")
                with self.assertRaises(EvaluationError) as raised:
                    execute(model, {}, {"extension": ".py"}, "sha256:test", solution_limit=1, execution_timeout=5,
                            compilation_timeout=5, memory_mb=256, cpus=1)
                self.assertEqual(raised.exception.reason, reason)
                self.assertIn(f"exited 137 ({readings})", raised.exception.detail)
                # The container outlives its exit only until it has been inspected.
                self.assertEqual(commands, ["run"] + ["inspect"] * inspections + ["rm"])

    def test_only_exit_137_rereads_the_oom_flag(self):
        """Another exit code is not a kill, so one unset reading settles it."""
        commands = []

        def docker(command, timeout):
            commands.append(command[1])
            return {"run": (1, "", "Traceback"), "inspect": (0, "false\n", ""), "rm": (0, "", "")}[command[1]]

        with tempfile.TemporaryDirectory() as temp, patch("evaluation.execution.run_process", side_effect=docker):
            model = Path(temp) / "model.py"
            model.write_text("# stub")
            with self.assertRaises(EvaluationError) as raised:
                execute(model, {}, {"extension": ".py"}, "sha256:test", solution_limit=1, execution_timeout=5,
                        compilation_timeout=5, memory_mb=256, cpus=1)
            self.assertEqual(raised.exception.reason, "execution_error")
            self.assertEqual(raised.exception.detail, "Runner exited 1: Traceback")
            self.assertEqual(commands, ["run", "inspect", "rm"])

    def test_legacy_framework_names_map_onto_integrations(self):
        """eval.py takes a framework name from a third party's JSONL. A known
        name maps onto an integration; an unknown one is passed through to fail
        as a missing integration, never run as arbitrary host Python."""
        self.assertEqual(solver_id("CPMpy"), "cpmpy_python")
        self.assertEqual(solver_id("or-tools"), "ortools_cp_sat_python")
        self.assertEqual(solver_id("z3"), "z3")

    def test_stop_at_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_text("# stub")
            records = [{"type": "solution", "values": {}}, {"type": "status", "status": "limit"}]
            with built_image(), patch("evaluation.check.execute", return_value=(records, {})) as execute:
                result = evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE,
                                  instances=[{"n": 3, "optimize": False}], instance_count=2)
                self.assertFalse(result["accepted"])
                self.assertEqual(result["unperformed_instances"], ["json:0"])
                self.assertEqual(execute.call_count, 1)

    def test_model_is_snapshotted(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.py"
            model.write_bytes(b"original")
            received = []
            def runner(path, instance, *args, **kwargs):
                received.append(kwargs["model_bytes"])
                model.write_bytes(b"changed during evaluation")
                return ([{"type": "solution", "values": {"x": 0, "y": instance["n"]}},
                         {"type": "status", "status": "limit"}], {})
            with built_image(), patch("evaluation.check.execute", side_effect=runner):
                result = evaluate(model, "tiny", "cpmpy_python", reference_source=SOURCE,
                                  instances=[{"n": 3, "optimize": False}], instance_count=2)
            self.assertTrue(result["accepted"], result)
            self.assertEqual(received, [b"original", b"original"])


class RecipeTests(unittest.TestCase):
    DOCKERFILE = ("FROM base@sha256:00 AS build\n"
                  "COPY --from=build /opt/x /opt/x\n"
                  "ADD --checksum=sha256:11 \\\n    https://example.org/x.jar /opt/x.jar\n"
                  "COPY --chmod=0755 runner/runtime.py \\\n    solvers/demo/run.py /opt/runner/\n"
                  "COPY solvers/demo/cpp /opt/cpp\n")

    def checkout(self, root):
        folder = root / "solvers" / "demo"
        (folder / "cpp" / "__pycache__").mkdir(parents=True)
        (root / "runner").mkdir()
        (folder / "metadata.json").write_text('{"id": "demo"}', encoding="utf-8")
        (folder / "Dockerfile").write_text(self.DOCKERFILE, encoding="utf-8")
        (folder / "run.py").write_text("run", encoding="utf-8")
        (folder / "cpp" / "main.cpp").write_text("int main() {}", encoding="utf-8")
        (folder / "cpp" / "__pycache__" / "x.pyc").write_bytes(b"stray")
        (root / "runner" / "runtime.py").write_text("runtime", encoding="utf-8")
        return folder

    def test_the_recipe_is_the_same_wherever_the_repository_is(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
            self.checkout(Path(one)); self.checkout(Path(two))
            self.assertEqual(recipe("demo", Path(one)), recipe("demo", Path(two)))

    def test_the_recipe_covers_every_copied_file_and_nothing_else(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = self.checkout(root)
            before = recipe("demo", root)
            (folder / "cpp" / "__pycache__" / "x.pyc").write_bytes(b"other")
            (folder / "notes.md").write_text("not copied", encoding="utf-8")
            self.assertEqual(recipe("demo", root), before)
            for path in (root / "runner" / "runtime.py", folder / "cpp" / "main.cpp", folder / "Dockerfile"):
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                self.assertNotEqual(recipe("demo", root), before, path)
                path.write_bytes(original)
            self.assertEqual(recipe("demo", root), before)

    def test_copied_files_are_hashed_in_the_same_order_on_every_platform(self):
        """Windows compares paths case-insensitively; the recipe must sort as POSIX does."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            folder = self.checkout(root)
            (folder / "Manifest.toml").write_text("manifest", encoding="utf-8")
            (folder / "driver.jl").write_text("driver", encoding="utf-8")
            with open(folder / "Dockerfile", "a", encoding="utf-8") as dockerfile:
                dockerfile.write("COPY solvers/demo/driver.jl solvers/demo/Manifest.toml /opt/\n")
            names = [path.name for path in _copied_sources(folder / "Dockerfile", root)]
            self.assertLess(names.index("Manifest.toml"), names.index("driver.jl"))

    def test_a_copied_file_missing_from_the_repository_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.checkout(root)
            (root / "runner" / "runtime.py").unlink()
            with self.assertRaises(EvaluationError):
                recipe("demo", root)


if __name__ == "__main__":
    unittest.main()
