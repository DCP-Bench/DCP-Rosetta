"""Essence' through Savile Row 1.11.1 to Minion, with the instance binding this integration adds.

The binding itself, which turns the JSON instance into an Essence' parameter file, is in dcp_convert_essence.py
(its docstring has the rules). It is a separate file because readers download it to prepare their own data; the
evaluator imports it, so both bind identically. A refusal is an `error` status with the reason as detail.

Savile Row runs from a fresh directory under /tmp. The solutions of every
`find` variable are read back from its solution files. Optimisation reports a
solution only when Minion finished its search (`SolverTimeOut:0`); Minion's info
file has no separate optimality key. While that search runs, each improving
solution's objective is reported as an incumbent (see `Incumbents`).
"""
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "/opt/runner")
sys.path.insert(0, str(Path(__file__).resolve().parent))  # dcp_convert_essence.py sits beside this file
import runtime
# generation.brief and next_work import refusal() from here, on the host
from dcp_convert_essence import comment_free, escape, literal, param_file, refusal, unescape  # noqa: E402,F401

STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here
# Seconds the first build took (Savile Row's translation, until the Minion input is
# written), and from STARTED until the request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0
BUILT = False

SAVILEROW = "/opt/savilerow"
# Objective bounds for the auxiliary variable used to read the optimum back.
BIG = 10 ** 12
































# --- reading solutions ------------------------------------------------------

TOKEN = re.compile(r"\s*(-?\d+|true|false|\[|\]|,|;)")


def parse_value(text):
    """Parse an Essence' literal: int, Boolean or nested matrix; an index
    domain after `;` is skipped, as every matrix is read as a JSON list."""
    pos = 0

    def token():
        nonlocal pos
        match = TOKEN.match(text, pos)
        if not match:
            raise ValueError(f"Cannot parse solution value near {text[pos:pos + 30]!r}")
        pos = match.end()
        return match.group(1)

    def value():
        nonlocal pos
        first = token()
        if first == "[":
            items = []
            while True:
                if TOKEN.match(text, pos) and TOKEN.match(text, pos).group(1) == "]":
                    token()
                    return items
                items.append(value())
                follow = token()
                if follow == ";":
                    depth = 0
                    while True:  # skip the index domain up to the closing bracket
                        char = text[pos]
                        pos += 1
                        depth += char == "("
                        depth -= char == ")"
                        if char == "]" and depth <= 0:
                            return items
                elif follow == "]":
                    return items
                elif follow != ",":
                    raise ValueError("Malformed matrix in solution file")
        if first in ("true", "false"):
            return first == "true"
        return int(first)

    result = value()
    if text[pos:].strip():
        raise ValueError(f"Trailing text in solution value: {text[pos:pos + 30]!r}")
    return result


def parse_solution(text):
    text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("$"))
    found = list(re.finditer(r"(?m)^letting\s+([A-Za-z][A-Za-z0-9_.]*)\s+(?:be|=)\s+", text))
    values = {}
    for i, match in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        values[match.group(1)] = parse_value(text[match.end():end].strip())
    return values


def read_info(path):
    info = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            key, _, value = line.partition(":")
            info[key.strip()] = value.strip()
    return info


# --- running Savile Row -----------------------------------------------------

OBJECTIVE = re.compile(r"(?m)^[ \t]*(minimising|maximising)[ \t]+(\S[^\n]*?)[ \t]*$")




def with_constraint(source, constraint):
    """Add one constraint after the model's last. Savile Row takes a single `such
    that` list, so a model that has one gets a comma, and one without gets the keyword."""
    if re.search(r"\bsuch\s+that\b", comment_free(source)):
        return source.rstrip() + f",\n{constraint}\n"
    return source.rstrip() + f"\nsuch that\n{constraint}\n"


def cells(value, prefix=()):
    """(1-based index, scalar) for every element of a solution value."""
    if isinstance(value, list):
        for position, item in enumerate(value, 1):
            yield from cells(item, prefix + (position,))
    else:
        yield prefix, value


def nogood(values):
    """A constraint that excludes one assignment of the declared outputs, matrices
    flattened to elements. None when there is nothing to exclude."""
    parts = []
    for name, value in values.items():
        for index, scalar in cells(value):
            target = escape(name) + (f"[{', '.join(map(str, index))}]" if index else "")
            literal = ("true" if scalar else "false") if isinstance(scalar, bool) else str(scalar)
            parts.append(f"{target} = {literal}")
    if not parts:
        return None
    conjunction = " /\\ ".join(parts)
    return "!(" + conjunction + ")"


class Incumbents:
    """Follows Minion's improving solutions during the optimisation run, as incumbents.

    Savile Row runs Minion with `-solsout .MINIONSOLS_*`, and Minion appends one line
    to that file per improving solution: the values of the Minion model's PRINT list,
    which ends with the variable of its MINIMISING or MAXIMISING line (Savile Row's
    auxiliary equal to the Essence' objective). Savile Row deletes the file when Minion
    is done, so Minion is started through minion-follow.sh, which gives it the second
    name FOLLOWED first. Only files are read, so the search is Savile Row's own. A
    line's seconds count from when the Minion model was written (the end of the build,
    as BUILD_SECONDS) to the solutions file's last change: exact for the last line
    read, an upper bound for an earlier one read in the same poll.

    The objective variable's value is the Essence' objective's own (Savile Row keeps its
    constant, sign and direction: `maximising 3 + x + y` gives 3, 4, 5), so the last line's,
    `last`, is the optimum once Minion has finished its search.
    """

    FOLLOWED = "dcp_incumbents.sols"

    def __init__(self, work):
        self.work, self.handle, self.position, self.start = work, None, None, None
        self.last = None

    def objective_position(self):
        """Index of the objective's value in a solution line, or None."""
        try:
            text = open(os.path.join(self.work, "out.minion"), encoding="utf-8").read()
            self.start = os.stat(os.path.join(self.work, "out.minion")).st_mtime
        except OSError:
            return None
        objective = re.search(r"(?m)^(?:MINIMISING|MAXIMISING)[ \t]+(\S+)[ \t]*$", text)
        printed = re.search(r"(?m)^PRINT[ \t]*(\[.*)$", text)
        if not objective or not printed:
            return None
        names = re.findall(r"[^\[\],\s]+", printed.group(1))
        if objective.group(1) not in names:
            return None
        # Savile Row appends the objective last; a decision variable may also appear earlier.
        return len(names) - 1 - names[::-1].index(objective.group(1))

    def poll(self):
        if self.handle is None:
            try:
                self.handle = open(os.path.join(self.work, self.FOLLOWED), "rb")
            except OSError:
                return  # Minion has not started yet
        while self.handle:
            offset = self.handle.tell()
            line = self.handle.readline()
            if not line.endswith(b"\n"):
                self.handle.seek(offset)  # not yet complete: read again next time
                return
            if self.position is None:
                # The first solution: Minion is running on the final out.minion.
                self.position = self.objective_position()
                if self.position is None:
                    self.close()  # no objective to follow
                    self.handle = False
                    return
            try:
                changed = os.fstat(self.handle.fileno()).st_mtime
                value = int(line.split()[self.position])
            except (IndexError, ValueError, OSError):
                continue
            self.last = value
            runtime.emit({"type": "incumbent", "objective": value,
                          "seconds": max(0.0, changed - self.start)})

    def close(self):
        if self.handle:
            self.handle.close()


# How often the optimisation run's incumbents are looked for.
POLL_SECONDS = 0.05


def savile_row(work, source, param, deadline, count, incumbents=None):
    """One Savile Row + Minion run. Returns (solutions, info, error). `solutions`
    is a list of dicts of every find variable; `count` caps them (`None` for an
    optimisation, which writes one). `incumbents`, an Incumbents on `work`, reports
    the run's improving solutions as they are found (the optimisation search proper only)."""
    global BUILD_SECONDS, BUILT
    for old in (glob.glob(os.path.join(work, "out*")) + glob.glob(os.path.join(work, ".MINION*"))
                + glob.glob(os.path.join(work, Incumbents.FOLLOWED))):
        os.remove(old)
    with open(os.path.join(work, "model.eprime"), "w", encoding="utf-8") as handle:
        handle.write(source)
    left = deadline - time.monotonic()
    if left <= 2:
        return None, {}, "timeout"
    seconds = max(1, int(left) - 2)
    command = ["java", "-XX:ParallelGCThreads=1", "-XX:+UseSerialGC", "-Xmx1200m",
               f"-Djava.library.path={SAVILEROW}/lib", "-jar", f"{SAVILEROW}/savilerow.jar",
               "model.eprime", "model.param", "-run-solver", "-minion-bin",
               "/opt/runner/minion-follow.sh" if incumbents else f"{SAVILEROW}/bin/minion",
               "-timelimit", str(seconds), "-solver-options", f"-cpulimit {seconds}",
               "-out-solution", "out.solution", "-out-info", "out.info", "-out-minion", "out.minion",
               "-out-aux", "out.aux"]
    if count is not None:
        command += ["-num-solutions", str(count)]
    launched = time.time()  # wall clock, as a file's mtime
    process = subprocess.Popen(command, cwd=work, stdout=sys.stderr, stderr=sys.stderr,
                               start_new_session=True)
    follow = incumbents
    stop = time.monotonic() + max(1, left)
    try:
        while True:
            try:
                process.wait(timeout=max(0.0, min(POLL_SECONDS if follow else stop, stop - time.monotonic())))
                break
            except subprocess.TimeoutExpired:
                if follow:
                    follow.poll()
                if time.monotonic() >= stop:
                    return None, {}, "timeout"
        if follow:
            follow.poll()
    finally:
        if follow:
            follow.close()
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                shutil.rmtree(work, ignore_errors=True)
            process.wait()
        minion = os.path.join(work, "out.minion")
        if not BUILT and os.path.isfile(minion):
            BUILD_SECONDS = max(0.0, os.stat(minion).st_mtime - launched)
        BUILT = True
    info = read_info(os.path.join(work, "out.info"))
    if info.get("SavileRowTimeOut") == "1":
        return None, info, "timeout"
    if process.returncode:
        return None, info, f"Savile Row exited {process.returncode}; see stderr"
    files = sorted(glob.glob(os.path.join(work, "out.solution*")))
    solutions = [parse_solution(open(path, encoding="utf-8").read()) for path in files]
    return [{unescape(name): value for name, value in solution.items()} for solution in solutions], info, None


def essence_solver(request):
    started = time.monotonic()
    deadline = started + request["execution_timeout"]
    source = open("/input/model.eprime", encoding="utf-8").read()
    work = tempfile.mkdtemp(prefix="essence_", dir="/tmp")
    try:
        param = param_file({} if request["legacy"] else request["instance"], source,
                           check=not request["legacy"])
        with open(os.path.join(work, "model.param"), "w", encoding="utf-8") as handle:
            handle.write(param)
        run(request, source, work, deadline)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def run(request, source, work, deadline):
    limit = request["solution_limit"]
    declared = request.get("outputs") or []
    seen, emitted = set(), []
    optimum = None  # an optimisation's proven optimum, which every solution it reports has

    def project(solution):
        if declared and all(name in solution for name in declared):
            return {name: solution[name] for name in declared}
        return solution

    def keep(solutions):
        for solution in solutions:
            values = project(solution)
            key = json.dumps(values, sort_keys=True)
            if key not in seen:
                seen.add(key)
                emitted.append(values)

    def flush(status, detail=""):
        for values in emitted[:limit]:
            record = {"type": "solution", "values": values}
            if optimum is not None:
                record["objective"] = optimum
            runtime.emit(record)
        return runtime.finish(status, detail)

    objectives = OBJECTIVE.findall(comment_free(source))
    optimising = bool(re.search(r"\b(minimising|maximising)\b", comment_free(source)))
    if optimising:
        follow = Incumbents(work)
        solutions, info, error = savile_row(work, source, None, deadline, None, incumbents=follow)
        if error == "timeout" or (not error and info.get("SolverTimeOut") != "0"):
            return runtime.finish("timeout", "Candidate optimum was not proven")
        if error:
            return runtime.finish("error", error)
        if not solutions:
            return runtime.finish("unsat")
        keep(solutions[:1])
        # The objective of Minion's last solution, the optimum. Where Minion had none to follow (an
        # objective Savile Row reduced to a constant), the probe below reads it.
        optimum = follow.last
        if limit == 1 and optimum is not None:
            return flush("limit")
        if len(objectives) != 1 or len(OBJECTIVE.findall(source)) != 1:
            if limit == 1:
                return runtime.finish("error", "Could not read the objective value: write `minimising EXPR` "
                                      "or `maximising EXPR` on its own line")
            return runtime.finish("unsupported", "Enumeration requires `minimising EXPR` or "
                                  "`maximising EXPR` on its own line")
        direction, expression = objectives[0]
        # Read the optimum through an auxiliary variable equal to the objective expression, then fix it.
        probe = OBJECTIVE.sub(lambda m: f"find dcp_objective_value : int({-BIG}..{BIG})\n"
                              f"{direction} dcp_objective_value", source, count=1)
        probe = with_constraint(probe, f"dcp_objective_value = ({expression})")
        solutions, info, error = savile_row(work, probe, None, deadline, None)
        if error == "timeout" or (not error and info.get("SolverTimeOut") != "0"):
            if optimum is None:
                return runtime.finish("timeout", "The objective value was not read back in time")
            return flush("timeout", "Candidate optimum was not proven")
        if error:
            return runtime.finish("error", error)
        if not solutions or "dcp_objective_value" not in solutions[0]:
            return runtime.finish("error", "Could not read the optimum back from Savile Row")
        value = solutions[0]["dcp_objective_value"]
        optimum = value
        if limit == 1:
            return flush("limit")
        source = with_constraint(OBJECTIVE.sub("", source, count=1), f"({expression}) = {value}")
    # Satisfaction, or an optimisation fixed at its proven optimum. Savile Row
    # enumerates every `find` variable, so an auxiliary one that the constraints
    # leave free repeats an output assignment. Each round asks for the solutions
    # still missing, and excludes every assignment found so far with a nogood, so
    # each round adds a new output assignment or shows that none remain.
    nogoods = []
    while True:
        want = limit - len(emitted)
        attempt = with_constraint(source, ",\n".join(nogoods)) if nogoods else source
        solutions, info, error = savile_row(work, attempt, None, deadline, want)
        if error == "timeout":
            return flush("timeout")
        if error:
            return runtime.finish("error", error)
        keep(solutions)
        if len(emitted) >= limit:
            return flush("limit")
        if info.get("SolverTimeOut") != "0":
            return flush("timeout")
        if len(solutions) < want:
            return flush("complete" if emitted else "unsat")
        for solution in solutions:
            text = nogood(project(solution))
            if text is None:
                return flush("complete")
            if text not in nogoods:
                nogoods.append(text)


def finish(status, detail="", **metadata):
    """runtime.finish with the benchmarking times. Writes the record itself, so that importing this
    module twice in one process (as rosetta-bench does) does not wrap an already wrapped finish."""
    runtime.emit({"type": "status", "status": status, "detail": detail, "build_seconds": BUILD_SECONDS,
                  "read_seconds": READ_SECONDS, "main_seconds": time.monotonic() - STARTED, **metadata})


def started_solving(request):
    """runtime.main has read the request when it calls python_solver."""
    global READ_SECONDS
    READ_SECONDS = time.monotonic() - STARTED


runtime.finish = finish
# runtime.main sends any kind it does not know to python_solver, so replacing it
# keeps main's request parsing, time budget, status and error handling unchanged.
runtime.python_solver = lambda kind, request: started_solving(request) or essence_solver(request)

if __name__ == "__main__":
    runtime.main("essence")
