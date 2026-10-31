"""Lock the Python packages of a built image into its integration's requirements.txt.

Run after a build whose image passed readiness: the lock is what the image
holds, frozen inside it, with the SHA-256 of the exact wheel pip selects there.
The Dockerfile then installs it with
`pip install --no-cache-dir --require-hashes --only-binary=:all: -r ...` (without
--only-binary when the lock says a package has no wheel), so a rebuild on any
machine installs the same files or fails.
"""
import argparse
from pathlib import Path
import subprocess

from .execution import integration, integration_folder

# Runs inside the image, so pip selects files for exactly its Python and platform.
# Prints "name==version sha256 kind" per package; nothing reaches the host. A
# package with no wheel on the index is locked by its source archive instead.
SCRIPT = r"""
import hashlib, pathlib, subprocess, sys, tempfile
frozen = subprocess.run([sys.executable, "-m", "pip", "freeze", "--exclude", "pip"],
                        capture_output=True, text=True, check=True).stdout.split()
for pin in frozen:
    for kind, flag in (("wheel", "--only-binary=:all:"), ("source", "--no-binary=:all:")):
        folder = pathlib.Path(tempfile.mkdtemp())
        done = subprocess.run([sys.executable, "-m", "pip", "download", "--quiet", "--no-deps", flag,
                               "-d", str(folder), pin], capture_output=True, text=True)
        files = list(folder.iterdir())
        if done.returncode == 0 and len(files) == 1:
            print(pin, hashlib.sha256(files[0].read_bytes()).hexdigest(), kind)
            break
    else:
        print(pin)
"""


def lock(solver_id, output=None):
    metadata = integration(solver_id)
    output = Path(output) if output else integration_folder(solver_id) / "requirements.txt"
    # Root and network only here, to read the image and fetch its wheels; never for a submission.
    done = subprocess.run(["docker", "run", "--rm", "--pull=never", "--user=0", "--entrypoint", "python",
                           metadata["image"], "-c", SCRIPT], capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"{solver_id}: freezing or downloading failed (a package with no wheel?):\n"
                         f"{done.stderr[-2000:]}")
    lines = [f"# Locked from {metadata['image']} by `python -m evaluation.lock {solver_id}`.",
             "# Every version is the one installed in the certified image; each hash is",
             "# the wheel pip selects for that image's Python and platform."]
    sources = []
    for pin, *found in sorted((line.split() for line in done.stdout.splitlines() if line.strip()),
                              key=lambda item: item[0].lower()):
        if "==" not in pin or not found:
            raise SystemExit(f"{solver_id}: {pin} is not a release on the index")
        digest, kind = found
        if kind == "source":
            sources.append(pin.split("==")[0])
        lines.append(f"{pin} \\\n    --hash=sha256:{digest}")
    if sources:
        # pip then builds these in the image, so the Dockerfile cannot pass --only-binary=:all:.
        lines.insert(3, f"# No wheel exists for {', '.join(sources)}: locked by source archive, built in the image.")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solver_ids", nargs="+")
    args = parser.parse_args()
    for solver_id in args.solver_ids:
        print(lock(solver_id))


if __name__ == "__main__":
    main()
