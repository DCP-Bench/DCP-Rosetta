from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
import sys

from generation import skills, behaviour

SOURCES = "# Sources" + chr(10) * 2 + "- <https://agentskills.io/specification>" + chr(10)


def write_sources(bundle):
    (bundle / "sources.md").write_text(SOURCES, encoding="utf-8")


class SkillWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(skills, "ROOT", self.root)
        self.patch.start(); self.addCleanup(self.patch.stop)
        self.bundle = self.root / "skills/test-skill"
        self.bundle.mkdir(parents=True)
        self.text = "---\nname: test-skill\ndescription: Test one bounded workflow.\n---\nOriginal instructions.\n"
        (self.bundle / "SKILL.md").write_text(self.text)
        (self.bundle / "evals").mkdir()
        (self.bundle / "evals/evals.json").write_text(json.dumps({"schema_version": 1, "skill_name": "test-skill", "evals": [
            {"id": "tiny", "prompt": "Test something.", "expected_output": "Evidence",
             "assertions": ["Output exists"]}]}))
        write_sources(self.bundle)
        self.run = self.root / "generation/runs/run"
        self.run.mkdir(parents=True)
        (self.run / "run.json").write_text("{}")

    def candidate(self, suffix="Correction"):
        candidate = self.root / "working/test-skill"
        candidate.mkdir(parents=True)
        (candidate / "SKILL.md").write_text(self.text + suffix)
        import shutil
        shutil.copytree(self.bundle / "evals", candidate / "evals")
        shutil.copy2(self.bundle / "sources.md", candidate / "sources.md")
        return candidate

    def checks(self, expression):
        path = self.root / "checks.json"
        path.write_text(json.dumps([{"argv": [sys.executable, "-c", expression, "{skill}"], "timeout": 10}]))
        return path

    def test_format_and_portability(self):
        self.assertEqual(skills.validate(self.bundle)["name"], "test-skill")
        (self.bundle / "SKILL.md").write_text(self.text + "[escape](../../missing.md)")
        with self.assertRaises(ValueError): skills.validate(self.bundle)

    def test_placeholder_links_are_not_files_but_missing_files_are_reported(self):
        """A template's [<install guide>](<URL>) is not a link; a link to a missing file is."""
        (self.bundle / "SKILL.md").write_text(self.text + "[<guide>](<URL>) [<example>](assets/<example>/README.md)")
        self.assertEqual(skills.validate(self.bundle)["name"], "test-skill")
        (self.bundle / "SKILL.md").write_text(self.text + "[examples](assets/)")
        with self.assertRaisesRegex(ValueError, "link a file in it"):
            skills.validate(self.bundle)

    def test_bundle_hashes_cover_every_file(self):
        """Attempt snapshots rely on these hashes, so nothing may be skipped."""
        expected = {"SKILL.md", "evals/evals.json", "sources.md"}
        self.assertEqual(set(skills.hashes(self.bundle)), expected)
        (self.bundle / "SKILL.md").write_text(self.text + "Edit")
        self.assertNotEqual(skills.hashes(self.bundle)["SKILL.md"], skills.hashes(self.candidate())["SKILL.md"])

    def test_regression_rejects_bad_skill_update(self):
        proposal = skills.propose("run", self.bundle, self.candidate("Skip evaluation"), "observed failure at run/log")
        checks = self.checks("import pathlib,sys; assert 'Skip evaluation' not in (pathlib.Path(sys.argv[1])/'SKILL.md').read_text()")
        self.assertEqual(skills.check_proposal(proposal, checks)["status"], "rejected")
        with self.assertRaises(ValueError): skills.apply(proposal)
        self.assertEqual((self.bundle / "SKILL.md").read_text(), self.text)

    def test_apply_requires_unchanged_evidence_and_base(self):
        proposal = skills.propose("run", self.bundle, self.candidate(), "API correction reproducer")
        checks = self.checks("import pathlib,sys; assert (pathlib.Path(sys.argv[1])/'SKILL.md').is_file()")
        self.assertEqual(skills.check_proposal(proposal, checks)["status"], "validated")
        (self.bundle / "SKILL.md").write_text(self.text + "Concurrent edit")
        with self.assertRaises(ValueError): skills.apply(proposal)
        (self.bundle / "SKILL.md").write_text(self.text)
        skills.apply(proposal)
        self.assertIn("Correction", (self.bundle / "SKILL.md").read_text())
        self.assertTrue((Path(proposal) / "previous-live-bundle/SKILL.md").is_file())

    def test_rosetta_skills_can_be_improved_through_proposals(self):
        """model-generator and solver-setup live in rosetta-skills/ and change by proposal."""
        import shutil
        moved = self.root / "rosetta-skills/test-skill"
        moved.parent.mkdir()
        shutil.move(self.bundle, moved)
        self.bundle = moved
        proposal = skills.propose("run", moved, self.candidate(), "API correction reproducer")
        checks = self.checks("import pathlib,sys; assert (pathlib.Path(sys.argv[1])/'SKILL.md').is_file()")
        self.assertEqual(skills.check_proposal(proposal, checks)["status"], "validated")
        skills.apply(proposal)
        self.assertIn("Correction", (moved / "SKILL.md").read_text())
        outside = self.root / "elsewhere/test-skill"
        shutil.copytree(moved, outside)
        shutil.rmtree(self.root / "working")
        with self.assertRaisesRegex(ValueError, "rosetta-skills"):
            skills.propose("run", outside, self.candidate("Again"), "evidence")

    def test_prepared_is_not_passed_and_evidence_required(self):
        output = self.root / "trial"
        behaviour.prepare(self.bundle, "tiny", output)
        self.assertFalse((output / "result.json").exists())
        assessment = self.root / "assessment.json"
        assessment.write_text(json.dumps({"assessor": "independent", "execution": "agent-run", "assertions": {}}))
        with self.assertRaises(ValueError): behaviour.assess(output, assessment)
        assessment.write_text(json.dumps({"assessor": "independent", "execution": "agent-run", "assertions": {
            "Output exists": {"passed": False, "observation": "Did not finish",
                              "evidence": [str(output / "prompt.md")]}}}))
        self.assertFalse(behaviour.assess(output, assessment)["passed"])

    def test_project_gate_requires_sources_and_cases(self):
        skills.validate(self.bundle, project=True)
        (self.bundle / "sources.md").unlink()
        with self.assertRaisesRegex(ValueError, "sources.md"):
            skills.validate(self.bundle, project=True)
        write_sources(self.bundle)
        # Evals are optional, as in the Agent Skills standard, but a manifest
        # that is present has to be usable.
        manifest = self.bundle / "evals/evals.json"
        kept = manifest.read_text()
        manifest.write_text('{"skill_name":"test-skill","evals":[]}')
        with self.assertRaisesRegex(ValueError, "list cases"):
            skills.validate(self.bundle, project=True)
        manifest.write_text('{"skill_name":"test-skill","evals":[{"id":"a","prompt":"p",'
                            '"expected_output":"o","assertions":[{"id":"x"}]}]}')
        with self.assertRaisesRegex(ValueError, "plain strings"):
            skills.validate(self.bundle, project=True)
        manifest.unlink()
        skills.validate(self.bundle, project=True)
        manifest.write_text(kept)

    def test_every_interface_is_linked_from_the_entrypoint(self):
        """A skill shared by a solver's bindings routes to one file per interface."""
        (self.bundle / "interfaces").mkdir()
        (self.bundle / "interfaces/python.md").write_text("# Python\n")
        with self.assertRaisesRegex(ValueError, "interfaces/python.md is not linked"):
            skills.validate(self.bundle)
        (self.bundle / "SKILL.md").write_text(self.text + "| [Python](interfaces/python.md) |\n")
        skills.validate(self.bundle)
        self.assertEqual(skills.interface_entry(self.bundle, "python"), self.bundle / "interfaces/python.md")

    def test_an_interface_may_be_a_folder_entered_through_its_readme(self):
        """An interface that needs several files gets interfaces/<interface>/README.md."""
        folder = self.bundle / "interfaces/java"
        folder.mkdir(parents=True)
        (folder / "README.md").write_text("# Java\n")
        (folder / "search.md").write_text("# Search\n")
        with self.assertRaisesRegex(ValueError, "interfaces/java/README.md is not linked from SKILL.md"):
            skills.validate(self.bundle)
        (self.bundle / "SKILL.md").write_text(self.text + "| [Java](interfaces/java/README.md) |\n")
        with self.assertRaisesRegex(ValueError, "interfaces/java/search.md is not linked from interfaces/java/README.md"):
            skills.validate(self.bundle)
        (folder / "README.md").write_text("# Java\n\n[Search](search.md)\n")
        skills.validate(self.bundle)
        self.assertEqual(skills.interface_entry(self.bundle, "java"), folder / "README.md")
        # The same interface as a file and as a folder is ambiguous.
        (self.bundle / "interfaces/java.md").write_text("# Java\n")
        (self.bundle / "SKILL.md").write_text(self.text + "[a](interfaces/java/README.md) [b](interfaces/java.md)\n")
        with self.assertRaisesRegex(ValueError, "both a file and a folder"):
            skills.validate(self.bundle)
        self.assertIsNone(skills.interface_entry(self.bundle, "java"))
        (self.bundle / "interfaces/java.md").unlink()
        (self.bundle / "SKILL.md").write_text(self.text + "| [Java](interfaces/java/README.md) |\n")
        (self.bundle / "interfaces/notes").mkdir()
        with self.assertRaisesRegex(ValueError, "not \\['notes'\\]"):
            skills.validate(self.bundle)

    def test_integration_skill_follows_where_the_integration_lives(self):
        """A flat integration has its own skill; one nested under its solver uses the
        solver's shared skill, in the interface its folder is named after."""
        from evaluation.execution import EvaluationError, integration_folders
        legacy = self.root / "solvers/old_python"
        (legacy / "skills/old-python").mkdir(parents=True)
        (legacy / "skills/old-python/SKILL.md").write_text(self.text)
        (legacy / "metadata.json").write_text('{"id": "old_python"}')
        (legacy / "readiness").mkdir()
        (legacy / "readiness/metadata.json").write_text("{}")  # part of old_python, not an integration
        (self.root / "solvers/new/skills/new").mkdir(parents=True)
        (self.root / "solvers/new/skills/new/SKILL.md").write_text(self.text)
        (self.root / "solvers/new/java").mkdir()
        (self.root / "solvers/new/java/metadata.json").write_text('{"id": "new_java"}')
        self.assertEqual(integration_folders(self.root),
                         {"new_java": self.root / "solvers/new/java", "old_python": legacy})
        self.assertEqual(skills.integration_skill(self.root, "old_python"),
                         ("solvers/old_python/skills/old-python", None))
        self.assertEqual(skills.integration_skill(self.root, "new_java"), ("solvers/new/skills/new", "java"))
        self.assertEqual(skills.integration_skill(self.root, "missing"), (None, None))
        (self.root / "solvers/new_java").mkdir()
        (self.root / "solvers/new_java/metadata.json").write_text('{"id": "new_java"}')
        with self.assertRaisesRegex(EvaluationError, "Two folders claim integration new_java"):
            integration_folders(self.root)

if __name__ == "__main__":
    unittest.main()
