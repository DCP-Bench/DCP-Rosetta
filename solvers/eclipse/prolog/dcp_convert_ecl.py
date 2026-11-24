"""dcp_convert_ecl.py: turn a DCP-Rosetta instance file into data files an ECLiPSe model can read.

    python dcp_convert_ecl.py problem.json

writes problem_1.dat, problem_2.dat, ... (one per instance in the file), next to it. Each holds the instance as one
ECLiPSe term, a list of Key-Value pairs written -(Key, Value), ending with a full stop; the model's run block reads
it with read/1 and hands it to `model(Instance, Vars, Outputs)`, which reads a field with
`memberchk(values-Values, Instance)`. Run a model on one:

    eclipse -b model.ecl -e "run('problem_1.dat'), halt"

This file is also the evaluator's own term writer (the runner imports it), so a reader runs on exactly the data the
evaluator used. It is self-contained: copy it anywhere. Integers and floats are numbers, true, false and null the
atoms of those names, strings ECLiPSe strings, arrays lists (0-based positions, no inherent index base) and nested
objects lists of Key-Value pairs.
"""
import json
import math
import sys
from pathlib import Path


def quoted(text, quote):
    """ECLiPSe quoted text: backslash escapes for the quote, backslash and controls."""
    pieces = [quote]
    for char in text:
        if char in (quote, "\\"):
            pieces.append("\\" + char)
        elif char == "\n":
            pieces.append("\\n")
        elif char == "\t":
            pieces.append("\\t")
        elif ord(char) < 32 or ord(char) == 127:
            pieces.append("\\%03o\\" % ord(char))
        else:
            pieces.append(char)
    pieces.append(quote)
    return "".join(pieces)


def term(value):
    """The ECLiPSe term for a JSON value.

    Integers (bignums too) and floats are numbers, true/false/null the atoms of
    those names, strings ECLiPSe strings, arrays lists, and objects lists of
    Key-Value pairs with atom keys. Pairs are written as -(Key, Value) so no
    operator declaration is needed to read them.
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Non-finite number in the instance: {value}")
        text = repr(value)
        if "e" in text:
            mantissa, exponent = text.split("e")
            if "." not in mantissa:
                mantissa += ".0"
            text = f"{mantissa}e{int(exponent)}"
        return text
    if isinstance(value, str):
        return quoted(value, '"')
    if isinstance(value, list):
        return "[" + ", ".join(term(item) for item in value) + "]"
    if isinstance(value, dict):
        return "[" + ", ".join(f"-({quoted(key, chr(39))}, {term(item)})"
                               for key, item in value.items()) + "]"
    raise ValueError(f"Cannot convert {type(value).__name__} to an ECLiPSe term")


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
