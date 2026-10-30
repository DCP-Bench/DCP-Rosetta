"""Explicitly build the pilot images; evaluation itself never builds images."""
import argparse
import subprocess

from .execution import PLATFORM, RECIPE_LABEL, ROOT, integration, integration_folder, integration_folders, recipe


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
        # The label is what readiness compares, so an image counts as current on
        # any machine that built it from the same files.
        subprocess.run(["docker", "build", f"--platform={PLATFORM}", "-t", metadata["image"],
                        "--label", f"{RECIPE_LABEL}={recipe(solver_id)}", *cache,
                        "-f", str(integration_folder(solver_id) / "Dockerfile"), str(ROOT)], check=True)


if __name__ == "__main__":
    main()
