"""dcp_convert_asp.py: turn a DCP-Rosetta instance file into ASP facts for clingo.

    python dcp_convert_asp.py problem.json

writes problem_1.lp, problem_2.lp, ... (one per instance in the file), next to it. Run a model on one:

    clingo model.lp problem_1.lp

This file is also the evaluator's own instance binder (the runner imports `facts` from it), so a reader runs on
exactly the facts the evaluator used. It is self-contained: copy it anywhere.

Every JSON field becomes ground facts, index positions first and the value last, with 0-based indices and one index
per list level: "demand": [250, 255] gives demand(0,250). demand(1,255). A leading capital would start an ASP
variable, so the first character after any leading underscores is lowered (N gives n, _SHIP gives _sHIP). A string
also arrives one character at a time, name_char(index..., position, "c"), so a model can take it apart. Empty lists
give no facts. Only integers, Booleans (the constants true and false) and strings are accepted.
"""
import json
import sys
from pathlib import Path


def predicate(key):
    """An instance field name as an ASP predicate name.

    ASP reads a leading capital as a variable, and several problems use fields
    like `N`, so the first character is lowered. clingo also reads `_SHIP` as a
    variable, so leading underscores are kept and the first character after them
    is lowered instead: `_SHIP` becomes `_sHIP`. A collision is refused rather
    than silently merged.
    """
    if not key or not key.replace("_", "").isalnum():
        raise ValueError(f"Instance field {key!r} is not usable as an ASP predicate name")
    lead = len(key) - len(key.lstrip("_"))
    return key[:lead] + key[lead].lower() + key[lead + 1:]


def term(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    raise ValueError(f"Instance values must be integers, Booleans or strings; got {value!r}")


CHARACTERS = "_char"


def facts(instance):
    """The instance as ground facts: name(index, ..., value).

    Every string value also gives one fact per character,
    name_char(index, ..., position, "c"), with 0-based positions. The character
    predicate of one field must not be the predicate of another; that is refused.
    """
    lines, names, spelled = [], {}, {}
    for key, value in instance.items():
        name = predicate(key)
        if name in names:
            raise ValueError(f"Instance fields {names[name]!r} and {key!r} collide as {name!r}")
        names[name] = key

        def walk(current, indices):
            if isinstance(current, dict):
                raise ValueError("Nested objects in instances are not supported")
            if isinstance(current, list):
                for position, item in enumerate(current):
                    walk(item, indices + [str(position)])
            else:
                lines.append(f"{name}({','.join(indices + [term(current)])}).")
                if isinstance(current, str):
                    spelled[name + CHARACTERS] = key
                    for position, character in enumerate(current):
                        arguments = indices + [str(position), term(character)]
                        lines.append(f"{name}{CHARACTERS}({','.join(arguments)}).")

        walk(value, [])
    for name, key in spelled.items():
        if name in names:
            raise ValueError(f"The characters of instance field {key!r} would be {name!r}, "
                             f"the predicate of instance field {names[name]!r}")
    return "\n".join(lines)


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
        target = source.with_name(f"{source.stem}_{number}.lp")
        try:
            target.write_text(facts(instance) + "\n")
        except ValueError as error:
            sys.exit(f"instance {number}: {error}")
        print("wrote", target)


if __name__ == "__main__":
    main(sys.argv)
