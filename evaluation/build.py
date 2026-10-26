"""Explicitly build the pilot images; evaluation itself never builds images."""
import argparse
import subprocess

from .execution import ROOT, integration, integration_folder, integration_folders


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solver_ids", nargs="*")
    args = parser.parse_args()
    ids = args.solver_ids or list(integration_folders())
    for solver_id in ids:
        metadata = integration(solver_id)
        subprocess.run(["docker", "build", "--platform=linux/amd64", "-t", metadata["image"],
                        "-f", str(integration_folder(solver_id) / "Dockerfile"), str(ROOT)], check=True)


if __name__ == "__main__":
    main()
