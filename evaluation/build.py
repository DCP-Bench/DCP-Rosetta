"""Explicitly build the pilot images; evaluation itself never builds images."""
import argparse
import subprocess

from .execution import PLATFORM, RECIPE_LABEL, ROOT, integration, integration_folder, integration_folders, recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solver_ids", nargs="*")
    args = parser.parse_args()
    ids = args.solver_ids or list(integration_folders())
    for solver_id in ids:
        metadata = integration(solver_id)
        # The label is what readiness compares, so an image counts as current on
        # any machine that built it from the same files.
        subprocess.run(["docker", "build", f"--platform={PLATFORM}", "-t", metadata["image"],
                        "--label", f"{RECIPE_LABEL}={recipe(solver_id)}",
                        "-f", str(integration_folder(solver_id) / "Dockerfile"), str(ROOT)], check=True)


if __name__ == "__main__":
    main()
