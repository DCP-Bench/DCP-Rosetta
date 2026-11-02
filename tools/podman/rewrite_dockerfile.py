"""Called by tools/podman/docker: podman 3.x (buildah) has no `ADD --checksum`.

Rewrites `ADD --checksum=sha256:H SRC DEST` into `ADD SRC DEST` followed by
`RUN echo 'H  DEST' | sha256sum -c -`, so the checksum is still enforced.
Reads a Dockerfile path and writes the rewritten file to stdout.
"""
import re
import sys
from pathlib import Path

PATTERN = r"^ADD[ \t]+--checksum=sha256:([0-9a-f]{64})[ \t]*((?:[^\n]*\\\n)*[^\n]*)\n"


def fix(match):
    sha, rest = match.group(1), match.group(2).replace("\\\n", " ").split()
    return f"ADD {' '.join(rest)}\nRUN echo '{sha}  {rest[-1]}' | sha256sum -c -\n"


sys.stdout.write(re.sub(PATTERN, fix, Path(sys.argv[1]).read_text(), flags=re.MULTILINE))
