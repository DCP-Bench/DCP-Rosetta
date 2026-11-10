"""Explicitly build the pilot images; evaluation itself never builds images.

Docker and podman build from each integration's Dockerfile. Apptainer converts the
docker-archives `evaluation.export` wrote where the images were built: pass their
folder as --archive.
"""
import argparse

from .engine import current
from .execution import integration, integration_folders, recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solver_ids", nargs="*")
    parser.add_argument("--gha-cache", action="store_true",
                        help="Reuse layers from the GitHub Actions cache; needs a docker-container builder")
    parser.add_argument("--archive", help="apptainer: the folder of <id>.tar files from evaluation.export")
    args = parser.parse_args()
    engine = current()
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
        engine.build(solver_id, metadata, recipe(solver_id), cache, archive=args.archive)


if __name__ == "__main__":
    main()
