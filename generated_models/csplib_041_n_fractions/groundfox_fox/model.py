# csplib_041_n_fractions: a FOX model for GroundFOX from DCP Rosetta.
#
# Find distinct non-zero digits such that the following equation holds: A / BC + D / EF + G /
# HI = 1 Here, BC, EF, and HI are two-digit numbers formed by B and C, E and F, and H and I,
# respectively.
#
# Print the values (A, B, C, D, E, F, G, H, I) that satisfy the equation above.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_041_n_fractions.json --check

# csplib_041_n_fractions: a FOX model for GroundFOX from DCP Rosetta.
#
# Find distinct non-zero digits A..I such that A/BC + D/EF + G/HI = 1, where BC, EF and HI are the
# two-digit numbers 10*B + C, 10*E + F and 10*H + I. Print (A, B, C, D, E, F, G, H, I).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

from fractions import Fraction

DIGITS = list(range(1, 10))
LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

# Allowed tuples of the one equation A/BC + D/EF + G/HI = 1 over non-zero digits (data, as the
# allowed tuples of a single constraint): row k gives the digit of each letter. The theory selects
# one row and forces its digits; the digits-distinct rule is written in FOX.
_TWO = [(10 * t + u, t, u) for t in DIGITS for u in DIGITS]
_BY_VALUE = {}
for _g in DIGITS:
    for _n, _t, _u in _TWO:
        _BY_VALUE.setdefault(Fraction(_g, _n), []).append((_g, _n, _t, _u))

ROWS = []
for _a in DIGITS:
    for _x, _b, _c in _TWO:
        for _d in DIGITS:
            for _y, _e, _f in _TWO:
                _rest = 1 - Fraction(_a, _x) - Fraction(_d, _y)
                for _g, _z, _h, _i in _BY_VALUE.get(_rest, []):
                    ROWS.append((_a, _b, _c, _d, _e, _f, _g, _h, _i))


def _pred(letter, digit):
    # unary input symbol: the rows in which this letter takes this digit
    return "P%s%d" % (letter, digit)


def _theory():
    lines = ["? k [Row(k)] : sel(k)."]
    for letter in LETTERS:
        for d in DIGITS:
            lines.append("! k [%s(k)] : ~sel(k) | %s(%d)." % (_pred(letter, d), letter, d))
        lines.append("? v [Dig(v)] : %s(v)." % letter)
        lines.append("! v [Dig(v)] : ! w [Dig(w) & ~(v = w)] : ~%s(v) | ~%s(w)." % (letter, letter))
    # the nine letters take pairwise distinct digits
    for p in range(9):
        for q in range(p + 1, 9):
            lines.append("! v [Dig(v)] : ~%s(v) | ~%s(v)." % (LETTERS[p], LETTERS[q]))
    return "\n".join(lines)


_INVOC = ["Row/1", "Dig/1"] + [_pred(L, d) + "/1" for L in LETTERS for d in DIGITS]
FOX = (
    "invocabulary { " + " ".join(_INVOC) + " }\n"
    "outvocabulary { A/1 B/1 C/1 D/1 E/1 F/1 G/1 H/1 I/1 sel/1 }\n"
    "theory {\n" + _theory() + "\n}\n"
)


def structure(instance):
    s = {"Row": list(range(len(ROWS))), "Dig": DIGITS}
    for col, letter in enumerate(LETTERS):
        for d in DIGITS:
            s[_pred(letter, d)] = [k for k, row in enumerate(ROWS) if row[col] == d]
    return s
