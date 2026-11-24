"""dcp_convert_idp.py: add a DCP-Rosetta instance to an FO(.) model as a structure.

    python dcp_convert_idp.py problem.json [model.idp]

The model defaults to model.idp. For each instance in the file it writes model_1.idp, model_2.idp, ... next to the
model: the model followed by `structure S:<its vocabulary>`, which gives every data symbol the instance's values
(0-based, as in the JSON) and sizes the index types the data sizes. Run one with the IDP-Z3 engine
(`pip install idp-engine`, which this script needs):

    idp-engine model_1.idp

This file is also the evaluator's own instance binder (the runner imports it), so a reader runs on exactly the data
the evaluator used. It is self-contained: copy it anywhere. The model must name its vocabulary and theory, and end
with a `main` procedure over the theory `T` and the structure `S`; see the contract.

The binding rules, as the runner applies them:


A submission is a plain FO(.) knowledge base (`vocabulary` + `theory`, optionally
its own `structure`), not a program, and is parsed as written. All instance data
arrives in a `structure` the runner generates, which is how FO(.) hands data to a
knowledge base. FO(.) type ranges must be integer literals, so that structure also
interprets the types the data sizes:

- Every instance field whose name matches a declared symbol is interpreted: a
  scalar as `n := 5.`, an array as `cost := {(0,0)->1, ...}.` with 0-based
  indices, a Boolean array as the set of its true tuples.
- An argument type of such a symbol that is declared `<: Int` and interpreted
  nowhere is sized from the array: `type Task <: Int` with `cost: Task * Person
  -> Int` and a 4x5 `cost` gives `Task := {0..3}. Person := {0..4}.`
- A type `Range_f` declared `<: Int` and interpreted nowhere, for an integer scalar
  field `f`, is `{1..f}`: `type Range_n <: Int` with `n: 8` gives `Range_n := {1..8}.`
- Any other such type `T` with a declared constant `T_size: () -> Int` is `{1..v}`,
  where `v` is the value the theory gives `T_size` from the data
  (`T_size() = 2 * k().`). The runner reads it from IDP-Z3's own simplification of
  the theory, with `T` provisionally empty, before solving.

- A ragged list of rows `F` binds padded with 0 (false) to the longest row, as a
  rectangular `F`, plus `F_len` with each row's real length. A list of mixed rows
  such as `[target, [cells...]]` binds one piece per column, `F_1`, `F_2`, ... (see
  `pieces`). Only the names a model declares are bound.
- Strings are bound as ids, by `string_ids`: a list of distinct strings is a vocabulary (its items become
  the ids 0, 1, ...); a string equal to a vocabulary item becomes its id; a list of words over an alphabet
  (a string of distinct letters) becomes a ragged list of letter ids (padded with 0); an ISO date becomes its
  day number (days since 1970-01-01). Any other string is refused, only in a declared field.
"""
import contextlib
import datetime
import json
import re
import sys
from pathlib import Path

try:  # refusal() needs neither the engine nor a redirected stdout: the generation tools import it on the host
    from idp_engine import IDP, Theory
except ImportError:
    IDP = Theory = None


# the first id of a vocabulary item or a letter: FO(.) index types start at 0, as the JSON positions do
BASE = 0


RANGE = "Range_"


SIZE = "_size"


INT_SET = "ℤ"


BOOL_SET = "𝔹"


class Unsupported(Exception):
    pass


def shape(value):
    """Dimensions of a rectangular list, or None for a ragged one."""
    if not isinstance(value, list):
        return ()
    if not value:
        return (0,)
    inner = {shape(item) for item in value}
    if len(inner) != 1 or None in inner:
        return None
    return (len(value),) + inner.pop()


def cells(value, prefix=()):
    if not isinstance(value, list):
        yield prefix, value
        return
    for index, item in enumerate(value):
        yield from cells(item, prefix + (index,))


def literal(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    raise Unsupported(f"instance values of type {type(value).__name__} cannot be bound into FO(.)")


def key(index):
    return str(index[0]) if len(index) == 1 else "(" + ",".join(map(str, index)) + ")"


def vocabulary(idp):
    if len(idp.vocabularies) != 1:
        raise ValueError("A submission must declare exactly one vocabulary")
    return next(iter(idp.vocabularies.items()))


def interpreted_by_model(idp):
    names = set()
    for structure in idp.structures.values():
        names.update(str(name) for name in structure.interpretations)
    return names


def layout(value):
    """(dimensions, scalar kinds) of a rectangular list or scalar, else None."""
    if not isinstance(value, list):
        return (), {scalar_kind(value)}
    parts = [layout(item) for item in value]
    if any(part is None for part in parts) or len({part[0] for part in parts}) > 1:
        return None
    return (len(value),) + (parts[0][0] if parts else ()), set().union(*(part[1] for part in parts))


def scalar_kind(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    return type(value).__name__


def column_class(column):
    classes = {"array" if isinstance(item, list) else scalar_kind(item) for item in column}
    return classes.pop() if len(classes) == 1 else None


def rows_of(value):
    return bool(value) and all(isinstance(row, list) for row in value)


def uniform(items):
    """(dimensions, kind) when every item has one shape and one scalar kind, else None."""
    if not items:
        return None
    shapes = [layout(item) for item in items]
    if any(found is None for found in shapes) or len({found[0] for found in shapes}) != 1:
        return None
    kinds = set().union(*(found[1] for found in shapes))
    return (shapes[0][0], kinds.pop()) if len(kinds) == 1 else None


def filled(dimensions, value):
    if not dimensions:
        return value
    return [filled(dimensions[1:], value) for _ in range(dimensions[0])]


def pieces(name, value, split=True):
    """The (key, rectangular value) pairs one instance field binds as, by these rules:

    1. A rectangular list binds unchanged; a list of rows also gives `<name>_len`.
    2. A ragged list of rows whose items share one shape and one scalar kind binds
       padded with 0 (False) to the longest row, plus `<name>_len`.
    3. Rows of one length whose columns differ in type bind one piece per column,
       `<name>_1`, `<name>_2`, ..., each by rules 1 and 2 without splitting again.
    4. Rows of unequal length whose first items are scalars bind as `<name>_1` (the
       first items) and `<name>_2` (the rest of each row, by rule 2).

    Anything else raises Unsupported. Strings and floats are not a shape problem here:
    literal() refuses them only in a field the model declares."""
    if not isinstance(value, list):
        return [(name, value)]
    shape = layout(value)
    if shape is not None and len(shape[1]) <= 1:
        return [(name, value)] + ([(f"{name}_len", [len(row) for row in value])]
                                  if rows_of(value) else [])
    if rows_of(value):
        found = uniform([item for row in value for item in row])
        if found is not None:
            dims, kind = found
            longest = max(len(row) for row in value)
            pad = filled(dims, False if kind == "bool" else 0)
            return [(name, [row + [pad] * (longest - len(row)) for row in value]),
                    (f"{name}_len", [len(row) for row in value])]
        width = len(value[0])
        if split and width and all(len(row) == width for row in value):
            columns = [[row[j] for row in value] for j in range(width)]
            classes = [column_class(column) for column in columns]
            if None not in classes and len(set(classes)) > 1:
                return [piece for j, column in enumerate(columns, 1)
                        for piece in pieces(f"{name}_{j}", column, split=False)]
        heads = [row[0] for row in value] if all(value) else []
        if split and heads and column_class(heads) not in (None, "array"):
            return (pieces(f"{name}_1", heads, split=False)
                    + pieces(f"{name}_2", [row[1:] for row in value], split=False))
    raise Unsupported(f"Instance field `{name}` is ragged or mixes types in a way this integration "
                      "cannot bind: only the shapes in the rules of pieces() are reshaped")


def refusal(name, value):
    """Why no model could bind this instance field, or None. generation.next_work asks
    this on the host for every instance field, so it never needs the engine."""
    try:
        pieces(name, value)
    except Unsupported as error:
        return str(error)
    return None


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
       ragged list (padded with 0, with `<field>_len`); the alphabet becomes the ids of
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


def bound_symbol(vocab, taken, name):
    decl = vocab.symbol_decls.get(name)
    return decl is not None and name not in taken and type(decl).__name__ == "SymbolDeclaration"


def open_type(vocab, taken, sort):
    """A type declared `<: Int` that neither the vocabulary nor a model structure interprets."""
    decl = vocab.symbol_decls.get(sort)
    return (decl is not None and type(decl).__name__ == "TypeDeclaration" and decl.interpretation is None
            and sort not in taken and str(decl.super_set) == INT_SET)


def bind(idp, instance, structure="_dcp_instance"):
    """The generated structure interpreting declared data symbols and index types. Only
    the pieces a model declares are bound: an undeclared field is never refused."""
    instance = string_ids(instance)
    vocab_name, vocab = vocabulary(idp)
    taken = interpreted_by_model(idp)
    fields, origin = {}, {}
    for name, value in instance.items():
        try:
            parts = pieces(name, value)
        except Unsupported:
            if bound_symbol(vocab, taken, name):
                raise
            continue
        for key_name, data in parts:
            if key_name in fields and bound_symbol(vocab, taken, key_name):
                raise Unsupported(f"instance fields `{origin[key_name]}` and `{name}` both bind "
                                  f"as `{key_name}`")
            fields[key_name], origin[key_name] = data, name
    lines, sizes = [], {}
    for name, value in fields.items():
        if not bound_symbol(vocab, taken, name):
            continue
        decl = vocab.symbol_decls[name]
        dims = shape(value)
        if dims is None:
            raise Unsupported(f"instance field {name} is ragged and cannot be bound")
        sorts = [str(sort) for sort in decl.sorts]
        if len(sorts) != len(dims):
            raise ValueError(f"{name} is declared with {len(sorts)} arguments but the instance "
                             f"field has {len(dims)} dimensions")
        for sort, size in zip(sorts, dims):
            if open_type(vocab, taken, sort):
                if sort.startswith(RANGE):
                    raise ValueError(f"type {sort} is {{1..{sort[len(RANGE):]}}}, so it cannot index "
                                     f"the instance array {name}, whose indices start at 0")
                if sizes.setdefault(sort, size) != size:
                    raise ValueError(f"type {sort} would be sized both {sizes[sort]} and {size}")
        boolean = str(decl.codomain) == BOOL_SET
        if not dims:
            lines.append(f"{name} := {literal(value)}.")
        elif boolean:
            true = [key(index) for index, item in cells(value) if literal(item) == "true"]
            lines.append(f"{name} := {{{', '.join(true)}}}.")
        else:
            pairs = [f"{key(index)}->{literal(item)}" for index, item in cells(value)]
            lines.append(f"{name} := {{{', '.join(pairs)}}}.")
    for sort, size in sizes.items():
        lines.append(f"{sort} := {{0..{size - 1}}}." if size else f"{sort} := {{}}.")
    for sort in vocab.symbol_decls:
        if sort.startswith(RANGE) and open_type(vocab, taken, sort):
            field = sort[len(RANGE):]
            bound = instance.get(field)
            if isinstance(bound, bool) or not isinstance(bound, int):
                raise ValueError(f"type {sort} is {{1..{field}}}, but {field} is not an integer "
                                 "scalar field of the instance")
            lines.append(f"{sort} := {{1..{bound}}}." if bound >= 1 else f"{sort} := {{}}.")
    return f"structure {structure}:{vocab_name} {{\n" + "\n".join(lines) + "\n}\n"


def sized(idp, source, structure):
    """`structure` plus `T := {1..v}.` for each open type T sized by a `T_size` constant."""
    _, vocab = vocabulary(idp)
    taken = interpreted_by_model(idp)
    pending = [sort for sort in vocab.symbol_decls
               if open_type(vocab, taken, sort) and not sort.startswith(RANGE)
               and sort + SIZE in vocab.symbol_decls
               and not re.search(rf"^{re.escape(sort)} := ", structure, re.M)]
    if not pending:
        return structure
    probe = structure.replace("\n}\n", "".join(f"\n{sort} := {{}}." for sort in pending) + "\n}\n")
    full = IDP.from_str(source + "\n" + probe)
    theory = Theory(*full.theories.values(), *full.structures.values())
    found = {}
    for sentence in theory.constraints:
        if type(sentence).__name__ != "AComparison" or len(sentence.sub_exprs) != 2:
            continue
        if [str(op) for op in getattr(sentence, "operator", [])] != ["="]:
            continue
        for symbol, value in (sentence.sub_exprs, sentence.sub_exprs[::-1]):
            if (type(symbol).__name__ == "AppliedSymbol" and not symbol.sub_exprs
                    and type(getattr(value, "py_value", None)) is int):
                found.setdefault(symbol.decl.name, value.py_value)
    for assignment in theory.assignments.values():
        sentence, value = assignment.sentence, assignment.value
        if (type(sentence).__name__ == "AppliedSymbol" and not sentence.sub_exprs
                and type(getattr(value, "py_value", None)) is int):
            found.setdefault(sentence.decl.name, value.py_value)
    lines = []
    for sort in pending:
        size = found.get(sort + SIZE)
        if size is None:
            raise ValueError(f"type {sort} is sized by {sort}{SIZE}, which the theory must define "
                             f"from instance data alone, as `{sort}{SIZE}() = <expression>.`")
        lines.append(f"{sort} := {{1..{size}}}." if size >= 1 else f"{sort} := {{}}.")
    return structure.replace("\n}\n", "".join("\n" + line for line in lines) + "\n}\n")


def main(argv):
    if len(argv) not in (2, 3):
        sys.exit(__doc__)
    if IDP is None:
        sys.exit("This needs the IDP-Z3 engine: pip install idp-engine")
    source = Path(argv[1])
    model = Path(argv[2] if len(argv) == 3 else "model.idp")
    text = model.read_text()
    instances = json.loads(source.read_text())
    if isinstance(instances, dict):
        instances = [instances]
    if not instances:
        print("No instances in this file: the model needs no data.")
    for number, instance in enumerate(instances, 1):
        target = model.with_name(f"{model.stem}_{number}.idp")
        try:
            with contextlib.redirect_stdout(sys.stderr):  # the engine prints diagnostics
                idp = IDP.from_str(text)
                structure = sized(idp, text, bind(idp, instance, "S"))
                IDP.from_str(text + "\n" + structure)  # parses, or raises
        except (Unsupported, ValueError) as error:
            sys.exit(f"instance {number}: {error}")
        target.write_text(text + "\n" + structure)
        print("wrote", target)


if __name__ == "__main__":
    main(sys.argv)
