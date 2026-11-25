# csplib_021_crossfigures: a FOX model for GroundFOX from DCP Rosetta.
#
# Crossfigures are the numerical equivalent of crosswords. You have a grid and some clues with
# numerical answers to place on this grid. Clues come in several different forms (for example:
# Across 1. 25 across times two, 2. five dozen, 5. a square number, 10. prime, 14. 29 across
# times 21 down ...).
#
# Here is the specific problem:
#
# ```text 1 2 3 4 5 6 7 8 9 --------------------------- 1 2 _ 3 X 4 _ 5 6 1 7 _ X 8 _ _ X 9 _
# 2 _ X 10 _ X 11 12 X _ 3 13 14 _ _ X 15 _ 16 _ 4 X _ X X X X X _ X 5 17 _ 18 19 X 20 21 _ 22
# 6 _ X 23 _ X 24 _ X _ 7 25 26 X 27 _ _ X 28 _ 8 29 _ _ _ X 30 _ _ _ 9 ```
#
# Here are the clues:
#
# ```text Across 1 27 across times two 4 4 down plus seventy-one 7 18 down plus four 8 6 down
# divided by sixteen 9 2 down minus eighteen 10 Dozen in six gross 11 5 down minus seventy 13
# 26 down times 23 across 15 6 down minus 350 17 25 across times 23 across 20 A square number
# 23 A prime number 24 A square number 25 20 across divided by seventeen 27 6 down divided by
# four 28 Four dozen 29 Seven gross 30 22 down plus 450
#
# Down 1 1 across plus twenty-seven 2 Five dozen 3 30 across plus 888 4 Two times 17 across 5
# 29 across divided by twelve 6 28 across times 23 across 10 10 across plus four 12 Three
# times 24 across 14 13 across divided by sixteen 16 28 down times fifteen 17 13 across minus
# 399 18 29 across divided by eighteen 19 22 down minus ninety-four 20 20 across minus nine 21
# 25 across minus fifty-two 22 20 down times six 26 Five times 24 across 28 21 down plus
# twenty-seven ```
#
# Print the solved crossfigure as a list of lists of integers (M), where each cell marked X in
# the grid holds 0. Every other cell holds a digit of an answer, and that digit may also be 0.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_021_crossfigures.json --check

# csplib_021_crossfigures: a FOX model for GroundFOX from DCP Rosetta.
#
# Crossfigures (CSPLib 021): a 9x9 grid of cells, some marked X (value 0). Every run of
# non-X cells is an answer (no leading zero) whose value is given by its clue: a constant,
# a square, a prime, or an arithmetic relation (plus, minus, times, exact division, product)
# with another answer. Print the solved grid as M[r][c], X cells holding 0.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

GRID = [
    "1 2 _ 3 X 4 _ 5 6",
    "7 _ X 8 _ _ X 9 _",
    "_ X 10 _ X 11 12 X _",
    "13 14 _ _ X 15 _ 16 _",
    "X _ X X X X X _ X",
    "17 _ 18 19 X 20 21 _ 22",
    "_ X 23 _ X 24 _ X _",
    "25 26 X 27 _ _ X 28 _",
    "29 _ _ _ X 30 _ _ _",
]
N = 9

# Clue for each answer, (direction, number): ("const", c) | ("square",) | ("prime",)
# | ("plus"|"minus"|"times"|"div", source, k) (target = source op k, exact division)
# | ("prod", source1, source2).
CLUES = {
    ("A", 1): ("times", ("A", 27), 2),
    ("A", 4): ("plus", ("D", 4), 71),
    ("A", 7): ("plus", ("D", 18), 4),
    ("A", 8): ("div", ("D", 6), 16),
    ("A", 9): ("minus", ("D", 2), 18),
    ("A", 10): ("const", 72),
    ("A", 11): ("minus", ("D", 5), 70),
    ("A", 13): ("prod", ("D", 26), ("A", 23)),
    ("A", 15): ("minus", ("D", 6), 350),
    ("A", 17): ("prod", ("A", 25), ("A", 23)),
    ("A", 20): ("square",),
    ("A", 23): ("prime",),
    ("A", 24): ("square",),
    ("A", 25): ("div", ("A", 20), 17),
    ("A", 27): ("div", ("D", 6), 4),
    ("A", 28): ("const", 48),
    ("A", 29): ("const", 1008),
    ("A", 30): ("plus", ("D", 22), 450),
    ("D", 1): ("plus", ("A", 1), 27),
    ("D", 2): ("const", 60),
    ("D", 3): ("plus", ("A", 30), 888),
    ("D", 4): ("times", ("A", 17), 2),
    ("D", 5): ("div", ("A", 29), 12),
    ("D", 6): ("times", ("A", 23), 48),
    ("D", 10): ("plus", ("A", 10), 4),
    ("D", 12): ("times", ("A", 24), 3),
    ("D", 14): ("div", ("A", 13), 16),
    ("D", 16): ("times", ("D", 28), 15),
    ("D", 17): ("minus", ("A", 13), 399),
    ("D", 18): ("div", ("A", 29), 18),
    ("D", 19): ("minus", ("D", 22), 94),
    ("D", 20): ("minus", ("A", 20), 9),
    ("D", 21): ("minus", ("A", 25), 52),
    ("D", 22): ("times", ("D", 20), 6),
    ("D", 26): ("times", ("A", 24), 5),
    ("D", 28): ("plus", ("D", 21), 27),
}


def _words():
    rows = [line.split() for line in GRID]
    words = {}
    for r in range(N):
        for c in range(N):
            tok = rows[r][c]
            if tok == "X":
                continue
            if c == 0 or rows[r][c - 1] == "X":
                if c + 1 < N and rows[r][c + 1] != "X":
                    cells, k = [], c
                    while k < N and rows[r][k] != "X":
                        cells.append((r, k))
                        k += 1
                    words[("A", int(tok))] = cells
            if r == 0 or rows[r - 1][c] == "X":
                if r + 1 < N and rows[r + 1][c] != "X":
                    cells, k = [], r
                    while k < N and rows[k][c] != "X":
                        cells.append((k, c))
                        k += 1
                    words[("D", int(tok))] = cells
    return words


def _is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


WORDS = _words()
KEYS = sorted(WORDS)
WID = {key: i for i, key in enumerate(KEYS)}
assert set(KEYS) == set(CLUES), "clue table does not match the grid"
assert all(2 <= len(WORDS[k]) <= 4 for k in KEYS), "answers are 2 to 4 digits"


def _domain(key):
    """Allowed values of one answer from its own clue and its length (no other clue used)."""
    length = len(WORDS[key])
    lo, hi = 10 ** (length - 1), 10 ** length
    spec = CLUES[key]
    if spec[0] == "const":
        vals = [spec[1]]
    elif spec[0] == "square":
        vals = [s * s for s in range(1, 1000)]
    elif spec[0] == "prime":
        vals = [p for p in range(lo, hi) if _is_prime(p)]
    else:
        vals = range(lo, hi)
    return [v for v in vals if lo <= v < hi]


DOM = {key: _domain(key) for key in KEYS}
DOMSET = {key: set(vals) for key, vals in DOM.items()}


def _relation(key):
    """Allowed tuples of the ONE constraint of clue `key`, over the own domains of its sources."""
    spec = CLUES[key]
    if spec[0] == "prod":
        a, b = spec[1], spec[2]
        return [a, b], [(x, z, x * z) for x in DOM[a] for z in DOM[b] if x * z in DOMSET[key]]
    op, src, k = spec
    tuples = []
    for x in DOM[src]:
        if op == "plus":
            y = x + k
        elif op == "minus":
            y = x - k
        elif op == "times":
            y = x * k
        else:  # exact division
            if x % k:
                continue
            y = x // k
        if y in DOMSET[key]:
            tuples.append((x, y))
    return [src], tuples


# RELS[j] = (target key, [source keys], tuples); one entry per arithmetic clue.
RELS = []
for _key in KEYS:
    if CLUES[_key][0] in ("const", "square", "prime"):
        continue
    _srcs, _tuples = _relation(_key)
    RELS.append((_key, _srcs, _tuples))
for _tgt, _srcs, _ in RELS:
    if len(_srcs) == 2:
        assert all(len(WORDS[k]) == 2 for k in _srcs), "products use 2-digit factors"


def _pair(v):
    """A value as (high, low): the answer's digits above the last two, and its last two."""
    return v // 100, v % 100


def _unsupported(srcs, tuples):
    """Source values (or pairs) of this one constraint with no target value at all."""
    if len(srcs) == 1:
        sup = {t[0] for t in tuples}
        return [x for x in DOM[srcs[0]] if x not in sup]
    ok = {(x, z) for x, z, _ in tuples}
    return [(x, z) for x in DOM[srcs[0]] for z in DOM[srcs[1]] if (x, z) not in ok]


UNSUP = [_unsupported(srcs, tuples) for _, srcs, tuples in RELS]


# Answer encoding: value = 100 * high + low. The high part is one-hot over the high digits
# (for a 2-digit answer it is the single value 0; for 3 digits 1..9; for 4 digits 10..99), the
# low part is one-hot over 0..99 (10..99 for a 2-digit answer). Both are tied to the grid
# cells by small digit ladders, so no answer is spelled out over its thousands of values.
def _hi_values(length):
    return {2: [0], 3: list(range(1, 10)), 4: list(range(10, 100))}[length]


def _lo_values(length):
    return list(range(10, 100)) if length == 2 else list(range(0, 100))


def _hi_name(length):
    return f"Hi{length}"


def _lo_name(length):
    return "Lo2" if length == 2 else "Lo"


def _cell_lines():
    lines = []
    for r in range(N):
        for c in range(N):
            if GRID[r].split()[c] == "X":
                lines.append(f"    ? g [Zero(g)] : M({r}, {c}, g).")
            else:
                lines.append(f"    ? g [Digit(g)] : M({r}, {c}, g).")
                lines.append(f"    ! g [Digit(g)] : ! h [Digit(h) & g ~= h] : ~M({r}, {c}, g) | ~M({r}, {c}, h).")
    return lines


def _word_lines(key):
    i = WID[key]
    length = len(WORDS[key])
    lines = [f"    ? h [{_hi_name(length)}(h)] : h{i}(h).",
             f"    ? l [{_lo_name(length)}(l)] : l{i}(l).",
             f"    ! h [{_hi_name(length)}(h)] : ! l [f{i}(h, l)] : ~h{i}(h) | ~l{i}(l)."]
    for p, (r, c) in enumerate(WORDS[key]):
        q = length - 1 - p  # power of ten of this cell
        if q >= 2:
            lines.append(f"    ! h [{_hi_name(length)}(h)] : ! g [hg{length}p{p}(h, g)] : ~h{i}(h) | M({r}, {c}, g).")
        else:
            lines.append(f"    ! l [{_lo_name(length)}(l)] : ! g [lg{q}(l, g)] : ~l{i}(l) | M({r}, {c}, g).")
    return lines


def _rel_lines(j, tgt, srcs):
    t = WID[tgt]
    if len(srcs) == 1:
        s = WID[srcs[0]]
        hi, lo = _hi_name(len(WORDS[srcs[0]])), _lo_name(len(WORDS[srcs[0]]))
        return [
            f"    ! h [{hi}(h)] : ! l [{lo}(l)] : ! y [rh{j}(h, l, y)] : ~h{s}(h) | ~l{s}(l) | h{t}(y).",
            f"    ! h [{hi}(h)] : ! l [{lo}(l)] : ! y [rl{j}(h, l, y)] : ~h{s}(h) | ~l{s}(l) | l{t}(y).",
            f"    ! h [{hi}(h)] : ! l [u{j}(h, l)] : ~h{s}(h) | ~l{s}(l).",
        ]
    a, b = WID[srcs[0]], WID[srcs[1]]
    return [
        f"    ! x [Hi2(x)] : ! u [Lo2(u)] : ! z [Hi2(z)] : ! v [Lo2(v)] : ! y [rh{j}(x, u, z, v, y)] : "
        f"~h{a}(x) | ~l{a}(u) | ~h{b}(z) | ~l{b}(v) | h{t}(y).",
        f"    ! x [Hi2(x)] : ! u [Lo2(u)] : ! z [Hi2(z)] : ! v [Lo2(v)] : ! y [rl{j}(x, u, z, v, y)] : "
        f"~h{a}(x) | ~l{a}(u) | ~h{b}(z) | ~l{b}(v) | l{t}(y).",
        f"    ! x [Hi2(x)] : ! u [Lo2(u)] : ! z [Hi2(z)] : ! v [n{j}(x, u, z, v)] : "
        f"~h{a}(x) | ~l{a}(u) | ~h{b}(z) | ~l{b}(v).",
    ]


def _theory():
    lines = _cell_lines()
    for key in KEYS:
        lines += _word_lines(key)
    for j, (tgt, srcs, _) in enumerate(RELS):
        lines += _rel_lines(j, tgt, srcs)
    return "\n".join(lines)


_inputs = ["Hi2/1", "Hi3/1", "Hi4/1", "Lo/1", "Lo2/1", "Digit/1", "Zero/1"]
_inputs += [f"hg{L}p{p}/2" for L in (3, 4) for p in range(L - 2)]
_inputs += ["lg0/2", "lg1/2"]
for _key in KEYS:
    _inputs.append(f"f{WID[_key]}/2")
for _j, (_tgt, _srcs, _) in enumerate(RELS):
    if len(_srcs) == 1:
        _inputs += [f"rh{_j}/3", f"rl{_j}/3", f"u{_j}/2"]
    else:
        _inputs += [f"rh{_j}/5", f"rl{_j}/5", f"n{_j}/4"]
_outputs = ["M/3"]
for _key in KEYS:
    _outputs += [f"h{WID[_key]}/1", f"l{WID[_key]}/1"]

FOX = (
    "invocabulary { " + " ".join(_inputs) + " }\n"
    "outvocabulary { " + " ".join(_outputs) + " }\n"
    "theory {\n" + _theory() + "\n}\n"
)
FLAGS = []


def _forbidden_pairs(key):
    """(high, low) pairs of this answer's range that its own clue does not allow."""
    length = len(WORDS[key])
    allowed = {_pair(v) for v in DOM[key]}
    return [(h, l) for h in _hi_values(length) for l in _lo_values(length) if (h, l) not in allowed]


def structure(instance):
    s = {"domain": range(100), "Digit": range(10), "Zero": [0],
         "Hi2": _hi_values(2), "Hi3": _hi_values(3), "Hi4": _hi_values(4),
         "Lo": _lo_values(3), "Lo2": _lo_values(2)}
    for L in (3, 4):
        for p in range(L - 2):
            q = L - 1 - p
            s[f"hg{L}p{p}"] = [(h, (h // 10 ** (q - 2)) % 10) for h in _hi_values(L)]
    for q in (0, 1):
        s[f"lg{q}"] = [(l, (l // 10 ** q) % 10) for l in range(100)]
    for key in KEYS:
        s[f"f{WID[key]}"] = _forbidden_pairs(key)
    for j, (_, srcs, tuples) in enumerate(RELS):
        if len(srcs) == 1:
            s[f"rh{j}"] = sorted({(*_pair(x), _pair(y)[0]) for x, y in tuples})
            s[f"rl{j}"] = sorted({(*_pair(x), _pair(y)[1]) for x, y in tuples})
            s[f"u{j}"] = sorted({_pair(x) for x in UNSUP[j]})
        else:
            s[f"rh{j}"] = sorted({(*_pair(x), *_pair(z), _pair(y)[0]) for x, z, y in tuples})
            s[f"rl{j}"] = sorted({(*_pair(x), *_pair(z), _pair(y)[1]) for x, z, y in tuples})
            s[f"n{j}"] = sorted({(*_pair(x), *_pair(z)) for x, z in UNSUP[j]})
    return s
