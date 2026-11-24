"""dcp_convert_mzn.py: turn a DCP-Rosetta instance file into data files MiniZinc can read.

    python dcp_convert_mzn.py problem.json

writes problem_1.json, problem_2.json, ... (one per instance in the file), next to it. Run a model on one:

    minizinc model.mzn problem_1.json

This file is also the evaluator's own instance binder (the runner imports `bind` from it), so a reader runs on
exactly the data the evaluator used. It is self-contained: copy it anywhere.

MiniZinc's data interface takes only rectangular arrays whose elements share one
type: it mixes Booleans, integers and floats, but not strings with numbers, and
not scalars with arrays. A dataset field outside that shape would fail before
any model runs, so each JSON instance field is bound by these rules. Every array
is indexed from 1, as MiniZinc indexes a JSON array.

1. A field MiniZinc accepts binds unchanged. When it is a nonempty list of
   lists, `<field>_len` (each row's length) is bound beside it, so a model that
   needs the row lengths of a field that is ragged in other instances runs on
   this one too. It is left out when an instance field already has that name.
2. A ragged list of rows, whose items all have one shape and whose scalars all
   have one type, binds as `<field>`, padded to the longest row with 0, false,
   0.0 or "" in every padded position, plus `<field>_len`. The items may be
   scalars (a 2-D array) or equal-shape arrays (one more dimension each).
3. A list of equal-length rows whose columns have different types (strings
   beside numbers, or scalars beside arrays) binds as one array per column,
   `<field>_1`, `<field>_2`, ..., numbered from 1; `<field>` itself is not
   bound. Each column then binds by rule 1 or rule 2, but is not split again.
4. A list of rows that each start with one scalar followed by any number of
   arrays (Kakuro's `[16, [1, 1], [1, 2]]`) binds as two fields:
   `<field>_1`, the first item of every row, and `<field>_2`, the rest of every
   row, bound by rule 1 or 2 (so a ragged rest is padded, with `<field>_2_len`).
   It is tried only after rules 1 to 3 fail, so no field they bind changes. A
   field whose rows all have the same length is bound by rule 3 instead, as
   `<field>_1`, `<field>_2`, ... one array per column.
5. Any other ragged or mixed field is refused, as is a generated name that is
   already an instance field or is generated twice.

A shape no rule covers stops the conversion with a message naming the instance field
(in the evaluator, an `error` status with that message as detail).
"""
import json
import sys
from pathlib import Path


class Unbindable(ValueError):
    pass


def kind(value):
    if isinstance(value, str):
        return "string"
    if isinstance(value, (bool, int, float)):
        return "number"
    return "other"


def layout(value):
    """(dimensions, scalar kinds) of a rectangular array or scalar, else None."""
    if not isinstance(value, list):
        return (), {kind(value)}
    parts = [layout(item) for item in value]
    if any(part is None for part in parts) or len({part[0] for part in parts}) > 1:
        return None
    inner = parts[0][0] if parts else ()
    return (len(value),) + inner, set().union(*(part[1] for part in parts))


def leaves(value):
    if isinstance(value, list):
        return [leaf for item in value for leaf in leaves(item)]
    return [value]


def pad_value(scalars):
    if scalars and all(isinstance(x, str) for x in scalars):
        return ""
    if scalars and all(isinstance(x, bool) for x in scalars):
        return False
    if any(isinstance(x, float) for x in scalars):
        return 0.0
    return 0


def filled(dimensions, value):
    if not dimensions:
        return value
    return [filled(dimensions[1:], value) for _ in range(dimensions[0])]


def column_class(column):
    """"array", "string" or "number" when the column is one of them, else None."""
    if all(isinstance(item, list) for item in column):
        return "array"
    kinds = {kind(item) for item in column}  # a list among scalars reads as "other"
    return kinds.pop() if len(kinds) == 1 and "other" not in kinds else None


def head_and_arrays(rows):
    """True when every row is one scalar followed by arrays, and some row has arrays."""
    return (all(row and kind(row[0]) != "other" and
                all(isinstance(item, list) for item in row[1:]) for row in rows)
            and any(len(row) > 1 for row in rows))


def field(name, value, split=True):
    """Yield (name, value, required) bindings for one instance field."""
    if not isinstance(value, list) or "other" in {kind(x) for x in leaves(value)}:
        yield name, value, True
        return
    rows = bool(value) and all(isinstance(row, list) for row in value)
    shape = layout(value)
    if shape is not None and len(shape[1]) <= 1:
        yield name, value, True
        if rows:
            yield f"{name}_len", [len(row) for row in value], False
        return
    if rows:
        items = [item for row in value for item in row]
        shapes = [layout(item) for item in items]
        if (items and None not in shapes and len({s[0] for s in shapes}) == 1
                and len(set().union(*(s[1] for s in shapes))) == 1):
            longest = max(len(row) for row in value)
            pad = filled(shapes[0][0], pad_value(leaves(items)))
            yield name, [row + [pad] * (longest - len(row)) for row in value], True
            yield f"{name}_len", [len(row) for row in value], True
            return
        width = len(value[0])
        if split and width and all(len(row) == width for row in value):
            columns = [[row[j] for row in value] for j in range(width)]
            classes = [column_class(column) for column in columns]
            if None not in classes and len(set(classes)) > 1:
                for j, column in enumerate(columns, 1):
                    yield from field(f"{name}_{j}", column, split=False)
                return
        if split and head_and_arrays(value):
            try:
                bindings = (list(field(f"{name}_1", [row[0] for row in value], split=False))
                            + list(field(f"{name}_2", [row[1:] for row in value], split=False)))
            except Unbindable:
                pass  # refused below, naming the instance field rather than a generated one
            else:
                yield from bindings
                return
    raise Unbindable(
        f"Instance field `{name}` is ragged or mixes types in a way this integration "
        "cannot bind: only a ragged list of rows with one item shape and one scalar "
        "type, equal-length rows whose columns differ in type, or rows of one scalar followed "
        "by arrays, are reshaped")


def bind(instance):
    required, optional = {}, {}
    for name, value in instance.items():
        for key, data, needed in field(name, value):
            if not needed:
                optional[key] = data
                continue
            if key in required or (key != name and key in instance):
                raise Unbindable(f"Instance field `{name}` binds as `{key}`, which is already "
                                 "an instance field or another generated name")
            required[key] = data
    for key, data in optional.items():
        if key not in instance and key not in required:
            required[key] = data
    return required


def refusal(name, value):
    """Why no model could be given this instance field, or None. The generation tools ask this on the host,
    for every instance field, to withhold problems an integration cannot bind."""
    try:
        list(field(name, value))
    except Unbindable as error:
        return str(error)
    return None


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
        target = source.with_name(f"{source.stem}_{number}.json")
        try:
            target.write_text(json.dumps(bind(instance)))
        except Unbindable as error:
            sys.exit(f"instance {number}: {error}")
        print("wrote", target)


if __name__ == "__main__":
    main(sys.argv)
