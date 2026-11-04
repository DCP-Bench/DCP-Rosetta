"""Export built images as docker-archives, for a machine that runs them with Apptainer.

    python -m evaluation.export --to DIR [ID ...]

writes DIR/<id>.tar for each built image (every integration by default). Copy DIR to
the Apptainer machine and convert it there with
`DCP_ENGINE=apptainer python -m evaluation.build --archive DIR [ID ...]`. The image
keeps its recipe label, so readiness still compares the same recipe there.
"""
import argparse
from pathlib import Path

from .engine import current
from .execution import integration, integration_folders


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solver_ids", nargs="*")
    parser.add_argument("--to", required=True, help="the folder to write <id>.tar into")
    args = parser.parse_args()
    engine = current()
    folder = Path(args.to)
    folder.mkdir(parents=True, exist_ok=True)
    for solver_id in args.solver_ids or list(integration_folders()):
        metadata = integration(solver_id)
        engine.image_recipe(metadata)  # fails clearly when the image was never built
        engine.save(metadata, folder / f"{solver_id}.tar")
        print(f"{solver_id}: {folder / f'{solver_id}.tar'}")


if __name__ == "__main__":
    main()
