"""Explicitly build the pilot images; evaluation itself never builds images."""
import argparse
import os
import re
import subprocess
import sys

from .execution import PLATFORM, RECIPE_LABEL, ROOT, integration, integration_folder, integration_folders, recipe

SECRET = re.compile(r"--mount=type=secret,id=([A-Za-z0-9_]+)")


def secrets(solver_id, root=ROOT):
    """The build secrets an integration's Dockerfile mounts, each with the variable naming its file.

    A secret (a solver licence) is never in the repository: DCP_SECRET_<ID> names the
    file on the building machine. The Dockerfile mounts it as optional, so the image
    still builds without it.
    """
    text = (integration_folder(solver_id, root) / "Dockerfile").read_text(encoding="utf-8")
    return [(name, f"DCP_SECRET_{name.upper()}") for name in sorted(set(SECRET.findall(text)))]


def missing_secrets(solver_id, root=ROOT):
    """The variables of an integration's build secrets that this environment does not set."""
    return [variable for _, variable in secrets(solver_id, root) if not os.environ.get(variable)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solver_ids", nargs="*")
    parser.add_argument("--gha-cache", action="store_true",
                        help="Reuse layers from the GitHub Actions cache; needs a docker-container builder")
    args = parser.parse_args()
    ids = args.solver_ids or list(integration_folders())
    for solver_id in ids:
        metadata = integration(solver_id)
        # One scope per image, or each build would replace the last one's cache.
        # mode=min stores only the image's own layers; a full hit skips earlier
        # stages anyway. A docker-container builder keeps the image unless loaded.
        cache = [f"--cache-from=type=gha,scope={solver_id}",
                 f"--cache-to=type=gha,scope={solver_id},mode=min,ignore-error=true", "--load"] if args.gha_cache else []
        # A layer holding a secret must not reach a remote cache, so the two never meet.
        passed = []
        for name, variable in secrets(solver_id):
            path = os.environ.get(variable)
            if path and not args.gha_cache:
                passed += ["--secret", f"id={name},src={path}"]
            else:
                reason = "--gha-cache would upload it" if path else f"{variable} is not set"
                print(f"{solver_id}: building without the {name} secret ({reason})", file=sys.stderr)
        # The label is what readiness compares, so an image counts as current on
        # any machine that built it from the same files.
        subprocess.run(["docker", "build", f"--platform={PLATFORM}", "-t", metadata["image"],
                        "--label", f"{RECIPE_LABEL}={recipe(solver_id)}", *cache, *passed,
                        "-f", str(integration_folder(solver_id) / "Dockerfile"), str(ROOT)], check=True)


if __name__ == "__main__":
    main()
