"""Run one toy model inside the Hexaly image: toyrun.py ROUND PROBLEM INSTANCE.

The instance path is a host path inside the exported toy folder; the container sees that
folder at /toy and the round's models at /m, both read-only, without network.
"""
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
IMAGE = os.environ.get("HEXALY_IMAGE", "hexaly-probe:dev")

round_dir, problem, instance = HERE / sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
inside = "/toy/" + instance.relative_to(HERE / "toy").as_posix()
command = ["docker", "run", "--rm", "--cpus", "1", "--network", "none", "--read-only",
           "--tmpfs", "/tmp:rw,exec,size=512m", "-e", "HOME=/tmp", "--workdir", "/tmp",
           "-v", f"{HERE / 'toy'}:/toy:ro", "-v", f"{round_dir / 'models'}:/m:ro",
           IMAGE, "python", f"/m/{problem}.py", inside]
sys.exit(subprocess.run(command, env={**os.environ, "MSYS_NO_PATHCONV": "1"}).returncode)
