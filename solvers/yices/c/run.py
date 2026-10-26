"""Runner for Yices submissions in C: compile model.c with the driver, run it, report.

The driver (/opt/c/driver.o, built from c/driver.c with the image) owns main(), the
solving, the optimality proof and the enumeration, and writes the protocol records. This
file compiles the submission, runs the candidate once, and turns a crash or a missing
status into an `error` record with the tail of the candidate's stderr.
"""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

sys.path.insert(0, "/opt/runner")
from runtime import finish

STATUS_WRITTEN = 79  # the driver's exit code after it wrote a status record
TAIL = 3000


def tail(text):
    text = text.strip()
    return text if len(text) <= TAIL else "..." + text[-TAIL:]


def main():
    request = json.loads(Path("/input/request.json").read_text())
    shutil.copyfile("/input/model.c", "/tmp/model.c")
    compile_command = ["gcc", "-std=gnu11", "-O2", "-I/opt/c", "-I/opt/yices/include",
                       "/tmp/model.c", "/opt/c/driver.o", "-L/opt/yices/lib",
                       "-lyices", "-lcjson", "-lgmp", "-lm", "-o", "/tmp/candidate"]
    try:
        compiled = subprocess.run(compile_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                  text=True, timeout=request["compilation_timeout"])
    except subprocess.TimeoutExpired:
        return finish("compilation_error", "Compilation timed out")
    print(compiled.stderr, file=sys.stderr)
    if compiled.returncode:
        return finish("compilation_error", "C compilation failed: " + tail(compiled.stderr))
    errors = open("/tmp/candidate.stderr", "w+")
    try:
        # The candidate inherits stdout: it writes the protocol records itself.
        result = subprocess.run(["/tmp/candidate"], input=json.dumps(request), text=True,
                                stderr=errors, timeout=request["execution_timeout"])
    except subprocess.TimeoutExpired:
        errors.seek(0)
        print(errors.read(), file=sys.stderr)
        return finish("timeout", "C execution exceeded limit")
    errors.seek(0)
    stderr = errors.read()
    print(stderr, file=sys.stderr)
    if result.returncode == STATUS_WRITTEN:
        return
    if result.returncode < 0:
        try:
            how = f"killed by signal {signal.Signals(-result.returncode).name}"
        except ValueError:
            how = f"killed by signal {-result.returncode}"
    else:
        how = f"exited with code {result.returncode} before reporting a status"
    finish("error", f"C process {how}. {tail(stderr)}".strip())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
