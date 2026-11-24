"""dcp_convert_essence.py: turn a DCP-Rosetta instance file into Essence' parameter files.

    python dcp_convert_essence.py problem.json [model.eprime]

writes problem_1.param, problem_2.param, ... (one per instance in the file), next to it. With a model (default:
model.eprime, if it exists) each file holds a `letting` for every `given` the model declares; without one, a
`letting` for every field an Essence' parameter can hold (integers, Booleans and matrices of them) and every
derived size. Run a model on one with Savile Row (which needs Java):

    savilerow model.eprime problem_1.param -run-solver

The solution is written to problem_1.param.solution. This file is also the evaluator's own instance binder (the
runner imports it), so a reader runs on exactly the data the evaluator used. It is self-contained: copy it anywhere.


The JSON instance becomes an Essence' parameter file. Only the fields the model
declares with `given` are bound, as `letting NAME = VALUE`: an instance field no
`given` names is ignored, whatever its type, so string metadata such as `name`
or `note` never reaches Savile Row. A declared given with no value is refused.
A model that needs a size which varies per instance declares `F_dim1`, `F_dim2`,
... beside a list field `F`; they bind the length along each axis of F after
reshaping. Matrices are indexed from 1, Booleans are `true`/`false`. Essence' has
no strings or floats (strings are bound as ids, rule 5) and a matrix literal must be rectangular, so a declared
field is bound by these rules:

1. An int, a Boolean, or a rectangular list of them binds unchanged. When it is a
   nonempty list of lists, `<field>_len` (each row's length) is available beside it.
2. A ragged list of rows whose items all have one shape and whose scalars all
   have one type binds as `<field>`, padded to the longest row with 0 or false,
   plus `<field>_len`. `<field>_dim1` is the outer length and `<field>_dim2` the
   padded longest row.
3. A list of equal-length rows whose columns have different types binds as one
   matrix per column, `<field>_1`, `<field>_2`, ...; `<field>` itself is not
   bound. Each column then binds by rule 1 or 2, but is not split again.
4. `<field>_dimK` (K from 1) is the length of a bound list along axis K, for every
   list bound by rules 1 to 3.
4b. Rows that each start with a scalar (one type) followed by a varying number of items, such as the cells of
   a clue `[target, [r, c], ...]`, bind as `<field>_1` (the leading scalars) and `<field>_2` (the rest of each
   row, by rule 1 or 2: padded, with `<field>_2_len`), as for equal-length rows in rule 3.
5. Strings are bound as ids, by `string_ids`: a list of distinct strings is a vocabulary (its items become the
   ids 1, 2, ...); a string equal to a vocabulary item becomes its id; a list of words over an alphabet (a
   string of distinct letters) becomes a ragged list of letter ids (rule 2, padded with 0); an ISO date becomes
   its day number (days since 1970-01-01).
6. Anything else that is declared is refused: floats, other strings, empty lists, names
   that are not Essence' identifiers, ragged or mixed fields outside rules 2 and 3.

Essence' reserved words cannot be names, so a field or output named `matrix` is
declared as `matrix_` (`given matrix_ : ...`, `find matrix_ : ...`). It binds under
that name, and a solution value `matrix_` is reported as `matrix`.

A refusal is an `error` status with the reason as detail.
"""
import datetime
import json
import re
import sys
from pathlib import Path


# Essence' and Savile Row words. A field or output with one of these names is written
# `<name>_` in the model, and binds or reads back under that name.
RESERVED = {"forall", "forAll", "exists", "sum", "such", "that", "letting", "given", "where",
            "find", "language", "int", "bool", "union", "intersect", "in", "false", "true",
            "matrix", "indexed", "by", "of", "be", "domain", "minimising", "maximising",
            "branching", "on", "heuristic", "toInt", "flatten", "table", "alldiff", "allDiff"}


# the first id of a vocabulary item or a letter: Essence' matrices start at 1
BASE = 1


GIVEN = re.compile(r"(?m)^[ \t]*given[ \t]+([^:\n]*):")


class Unbindable(ValueError):
    pass


def kind(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    return "float" if isinstance(value, float) else "string" if isinstance(value, str) else "other"


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


def filled(dimensions, value):
    if not dimensions:
        return value
    return [filled(dimensions[1:], value) for _ in range(dimensions[0])]


def column_class(column):
    kinds = {"array" if isinstance(item, list) else kind(item) for item in column}
    return kinds.pop() if len(kinds) == 1 else None


def field(name, value, split=True):
    """Yield (name, value, required) bindings for one instance field. Derived
    names (`_len`) are never required: they bind only when a given declares them."""
    if not isinstance(value, list):
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
            pad = filled(shapes[0][0], False if kind(leaves(items)[0]) == "bool" else 0)
            yield name, [row + [pad] * (longest - len(row)) for row in value], True
            yield f"{name}_len", [len(row) for row in value], False
            return
        width = len(value[0])
        if split and width and all(len(row) == width for row in value):
            columns = [[row[j] for row in value] for j in range(width)]
            classes = [column_class(column) for column in columns]
            if None not in classes and len(set(classes)) > 1:
                for j, column in enumerate(columns, 1):
                    yield from field(f"{name}_{j}", column, split=False)
                return
    if split and rows and all(row and not isinstance(row[0], list) for row in value) \
            and len({kind(row[0]) for row in value}) == 1:
        # rows of a leading scalar and a varying number of cells, `[target, [r, c], ...]`: one piece per part
        try:
            pieces = (list(field(f"{name}_1", [row[0] for row in value], split=False))
                      + list(field(f"{name}_2", [row[1:] for row in value], split=False)))
        except Unbindable:
            pieces = None  # the rest of the rows has no shape either: refused below, under the field's own name
        if pieces is not None:
            yield from pieces
            return
    raise Unbindable(
        f"Instance field `{name}` is ragged or mixes types in a way this integration "
        "cannot bind: only a ragged list of rows with one item shape and one scalar "
        "type, or equal-length rows whose columns differ in type, are reshaped")


def bindings(name, value):
    """field(), plus `<key>_dim1`, `<key>_dim2`, ... (the length along each axis of
    every required list, after reshaping) as optional bindings."""
    for key, data, needed in field(name, value):
        yield key, data, needed
        shape = layout(data) if needed and isinstance(data, list) else None
        for axis, length in enumerate(shape[0] if shape else (), 1):
            yield f"{key}_dim{axis}", length, False


def declared_givens(source):
    """Names declared by `given` lines, comma-separated lists included, comments ignored."""
    names = []
    for match in GIVEN.finditer(comment_free(source)):
        names += [part.strip() for part in match.group(1).split(",") if part.strip()]
    return names


def escape(name):
    """The Essence' name a field binds under: a reserved word gets a trailing `_`."""
    return name + "_" if name in RESERVED else name


def unescape(name):
    return name[:-1] if name.endswith("_") and name[:-1] in RESERVED else name


ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def string_leaves(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from string_leaves(item)


def map_strings(value, convert):
    if isinstance(value, str):
        return convert(value)
    return [map_strings(item, convert) for item in value] if isinstance(value, list) else value


def day_number(text):
    return (datetime.date.fromisoformat(text) - datetime.date(1970, 1, 1)).days


def is_date(text):
    try:
        return bool(ISO_DATE.fullmatch(text)) and day_number(text) is not None
    except ValueError:
        return False


def string_ids(instance):
    """The instance with its string data replaced by ids, so the rules below can bind it. Strings no rule
    covers stay strings (and are refused when a model declares them); ids start at BASE.

    1. A list of distinct strings is a vocabulary: it becomes the ids of its items, in order.
    2. A string equal to an item of a vocabulary (a cable's endpoints, in a list of rows) becomes that item's id.
    3. A list of words over an alphabet (a string of distinct letters) becomes the letter ids of each word, a
       ragged list (rule 2 of the shapes below, padded, with `<field>_len`); the alphabet becomes the ids of
       its letters.
    4. An ISO date (`2024-05-01`) becomes its day number, the days since 1970-01-01."""
    out = dict(instance)
    for name, value in instance.items():
        found = list(string_leaves(value))
        if found and all(is_date(text) for text in found):
            out[name] = map_strings(value, day_number)
    alphabets = {name: value for name, value in out.items()
                 if isinstance(value, str) and len(value) > 1 and len(set(value)) == len(value)}
    used = set()
    for name, value in list(out.items()):
        if isinstance(value, list) and value and all(isinstance(word, str) and word for word in value):
            for alphabet_name, alphabet in alphabets.items():
                if all(letter in alphabet for word in value for letter in word):
                    out[name] = [[alphabet.index(letter) + BASE for letter in word] for word in value]
                    used.add(alphabet_name)
                    break
    for alphabet_name in used:
        out[alphabet_name] = list(range(BASE, BASE + len(alphabets[alphabet_name])))
    vocabularies = {name: value for name, value in out.items()
                    if isinstance(value, list) and value and all(isinstance(item, str) for item in value)
                    and len(set(value)) == len(value)}
    used = set()
    for name, value in list(out.items()):
        found = set(string_leaves(value))
        if not found or name in vocabularies:
            continue
        for vocabulary_name, items in vocabularies.items():
            if found <= set(items):
                out[name] = map_strings(value, lambda text, items=items: items.index(text) + BASE)
                used.add(vocabulary_name)
                break
    for vocabulary_name in used:
        out[vocabulary_name] = list(range(BASE, BASE + len(vocabularies[vocabulary_name])))
    return out


def bind(instance, declared):
    """The bindings the model declares, by canonical name. Fields and derived names
    the model does not declare are never bound, so they cannot be refused."""
    instance = string_ids(instance)
    wanted = {unescape(name) for name in declared}
    relevant = {name: value for name, value in instance.items()
                if name in wanted or any(d.startswith(name + "_") for d in wanted)}
    required, optional = {}, {}
    for name, value in relevant.items():
        for key, data, needed in bindings(name, value):
            if not needed:
                optional[key] = data
                continue
            if key in required or (key != name and key in instance):
                raise Unbindable(f"Instance field `{name}` binds as `{key}`, which is already "
                                 "an instance field or another generated name")
            required[key] = data
    for key, data in optional.items():
        if key in wanted and key not in instance and key not in required:
            required[key] = data
    return {key: data for key, data in required.items() if key in wanted}


def refusal(name, value):
    """Why run.py cannot reshape this instance field on its own, or None. For a caller
    that must know whether any model could be given the field, without a model. A
    string is not a reshaping problem: it is refused only when a model declares the
    field as a given (see literal()), so a model that ignores the field is unaffected."""
    try:
        list(bindings(name, value))
    except Unbindable as error:
        return str(error)
    return None


def literal(name, value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        if not value:
            raise Unbindable(f"Instance field `{name}` contains an empty list, which an "
                             "Essence' matrix literal cannot express")
        return "[" + ", ".join(literal(name, item) for item in value) + "]"
    raise Unbindable(f"Instance field `{name}` holds a {kind(value)} value; Essence' parameters "
                     "are integers, Booleans and matrices of them")


def param_file(instance, source, check=True):
    """The parameter file for the givens `source` declares. With `check`, a declared
    given that the instance does not provide is refused."""
    declared = declared_givens(source)
    values = bind(instance, declared)
    if check:
        missing = [name for name in dict.fromkeys(declared) if unescape(name) not in values]
        if missing:
            raise Unbindable("Declared given " + ", ".join(f"`{name}`" for name in missing)
                             + " has no value: the instance has no such field, and no field "
                             "it is a size of")
    lines = ["language ESSENCE' 1.0"]
    for name, value in values.items():
        escaped = escape(name)
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", escaped):
            raise Unbindable(f"Instance field `{name}` is not usable as an Essence' identifier")
        lines.append(f"letting {escaped} = {literal(name, value)}")
    return "\n".join(lines) + "\n"


def comment_free(source):
    return re.sub(r"\$[^\n]*", "", source)


def param_file_all(instance):
    """A parameter file with every field of the instance that a parameter can hold, and every derived size."""
    instance = string_ids(instance)
    names = set()
    for name, value in instance.items():
        try:
            names.update(key for key, _, _ in bindings(name, value))
        except Unbindable:
            pass
    lines = ["language ESSENCE' 1.0"]
    for name, value in bind(instance, names).items():
        try:
            lines.append(f"letting {escape(name)} = {literal(name, value)}")
        except Unbindable:
            pass
    return "\n".join(lines) + "\n"


def main(argv):
    if len(argv) not in (2, 3):
        sys.exit(__doc__)
    source = Path(argv[1])
    model = Path(argv[2] if len(argv) == 3 else "model.eprime")
    text = model.read_text() if model.exists() else None
    instances = json.loads(source.read_text())
    if isinstance(instances, dict):
        instances = [instances]
    if not instances:
        print("No instances in this file: the model needs no data file.")
    for number, instance in enumerate(instances, 1):
        target = source.with_name(f"{source.stem}_{number}.param")
        try:
            target.write_text(param_file(instance, text) if text is not None else param_file_all(instance))
        except Unbindable as error:
            sys.exit(f"instance {number}: {error}")
        print("wrote", target)


if __name__ == "__main__":
    main(sys.argv)
