"""dcp_convert_picat.py: turn a DCP-Rosetta instance file into data files a Picat model can read.

    python dcp_convert_picat.py problem.json

writes problem_1.dat, problem_2.dat, ... (one per instance in the file), next to it. Each holds the instance as one
Picat term, json_object([Keys], [Values]).; the model's run block reads it, builds the map the model's
`model(Data, Vars, Outputs, Options)` expects (see the model's header) and solves. Run a model on one:

    picat model.pi problem_1.dat

This file is also the evaluator's own term writer (the runner imports it), so a reader runs on exactly the data
the evaluator used. It is self-contained: copy it anywhere. An integer is a Picat integer, JSON true and false are 1
and 0 (Picat has no Boolean type), a string is a Picat string, an array is a list (indexed from 1), null is the atom
null and a nested object is json_object(...) again.
"""
import json
import math
import sys
from pathlib import Path


def atom(text):
    """A quoted Picat atom, which is what every instance key becomes."""
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def string(text):
    escaped = []
    for char in text:
        if char in "\\\"":
            escaped.append("\\" + char)
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\t":
            escaped.append("\\t")
        elif ord(char) < 32:
            raise ValueError(f"Instance string holds control character {ord(char)}, which has no Picat escape here")
        else:
            escaped.append(char)
    return '"' + "".join(escaped) + '"'


def term(value):
    """The instance value as Picat term text for read_term/1.

    Arrays become lists and objects json_object(Keys, Values), which the driver
    turns into maps. Picat has no Boolean type, and its constraints read 1 as
    true, so JSON true and false become 1 and 0.
    """
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Instance holds a non-finite number")
        return repr(value)
    if isinstance(value, str):
        return string(value)
    if value is None:
        return "null"
    if isinstance(value, list):
        return "[" + ", ".join(term(item) for item in value) + "]"
    if isinstance(value, dict):
        keys = ", ".join(atom(key) for key in value)
        values = ", ".join(term(item) for item in value.values())
        return f"json_object([{keys}], [{values}])"
    raise ValueError(f"Instance value of type {type(value).__name__} is not JSON")


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    source = Path(argv[1])
    instances = json.loads(source.read_text())
    if isinstance(instances, dict):
        instances = [instances]
    if not instances:
        print("No instances in this file: the model needs no data file.")
    for number, instance in enumerate(instances, 1):
        target = source.with_name(f"{source.stem}_{number}.dat")
        try:
            target.write_text(term(instance) + ".\n")
        except ValueError as error:
            sys.exit(f"instance {number}: {error}")
        print("wrote", target)


if __name__ == "__main__":
    main(sys.argv)
