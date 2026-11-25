# contracting_costs: a FOX model for GroundFOX from DCP Rosetta.
#
# A contractor planning the construction of a house found that he would have to pay:
#
# * $ 1,100 to the paper hanger and the painter, * $ 1,700 to the painter and plumber, * $
# 1,100 to the plumber and electrician, * $ 3,300 to the electrician and carpenter, * $ 5,300
# to the carpenter and mason, * $ 3,200 to the mason and painter.
#
# What does each man charge for his services?
#
# Print the cost of each person's service (paper_hanger, painter, plumber, electrician,
# carpenter, mason) in dollars.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py contracting_costs.json --check

# Costs of the six pairwise payments (from the description): each pair's two charges sum to the payment.
#
# Encoding: every charge is a one-hot over its value range (the declared output), tied to base-10
# digit atoms; each payment is a column-wise addition of two charges with carry atoms. The addition
# tables and the per-position digit relations are data relations computed in structure.
PEOPLE = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
PAIRS = [
    ("paper_hanger", "painter", 1100),
    ("painter", "plumber", 1700),
    ("plumber", "electrician", 1100),
    ("electrician", "carpenter", 3300),
    ("carpenter", "mason", 5300),
    ("mason", "painter", 3200),
]
# Charges are positive and each is below the smallest payment it takes part in.
CAP = {p: min(c for a, b, c in PAIRS if p in (a, b)) - 1 for p in PEOPLE}
TOP = max(c for _, _, c in PAIRS)
NDIG = len(str(TOP))  # digit positions 0..NDIG-1 (least significant first)
BASE = 10


def _digit(v, q):
    return (v // BASE ** q) % BASE


def _theory():
    lines = []
    for p in PEOPLE:
        d = f"d_{p}"
        lines.append(f"    ? v [Cap_{p}(v)] : {p}(v).")
        lines.append(f"    ! v [Val(v) & ~Cap_{p}(v)] : ~{p}(v).")
        lines.append(f"    ! v [Cap_{p}(v)] : ! q [Dpos(q)] : ! x [DigOf(v, q, x)] : ~{p}(v) | {d}(q, x).")
        lines.append(f"    ! q [Dpos(q)] : ? x [Dig(x)] : {d}(q, x).")
        lines.append(f"    ! q [Dpos(q)] : ! x [Dig(x)] : ! y [Dig(y) & x ~= y] : ~{d}(q, x) | ~{d}(q, y).")
    for i, (a, b, _) in enumerate(PAIRS):
        c = f"cy_{i}"
        da, db = f"d_{a}", f"d_{b}"
        lines.append(f"    ! q [Cpos(q)] : ? k [Bit(k)] : {c}(q, k).")
        lines.append(f"    ! q [Cpos(q)] : ! k [Bit(k)] : ! k2 [Bit(k2) & k ~= k2] : ~{c}(q, k) | ~{c}(q, k2).")
        lines.append(f"    ! q [Zero(q)] : ~{c}(q, 1).")
        lines.append(f"    ! q [Last(q)] : ~{c}(q, 1).")
        lines.append(f"    ! q [Dpos(q)] : ! r [Nxt(q, r)] : ! x [Dig(x)] : ! y [Dig(y)] : ! k [Bit(k)] : "
                     f"! o [Ok{i}(q, x, y, k, o)] : ~{da}(q, x) | ~{db}(q, y) | ~{c}(q, k) | {c}(r, o).")
        lines.append(f"    ! q [Dpos(q)] : ! x [Dig(x)] : ! y [Dig(y)] : ! k [Bad{i}(q, x, y, k)] : "
                     f"~{da}(q, x) | ~{db}(q, y) | ~{c}(q, k).")
    return "\n".join(lines)


_OUT = []
for _p in PEOPLE:
    _OUT += [f"{_p}/1", f"d_{_p}/2"]
for _i in range(len(PAIRS)):
    _OUT.append(f"cy_{_i}/2")
_IN = ["Val/1", "Dig/1", "Dpos/1", "Cpos/1", "Nxt/2", "Bit/1", "DigOf/3", "Zero/1", "Last/1"]
_IN += [f"Cap_{p}/1" for p in PEOPLE]
for _i in range(len(PAIRS)):
    _IN += [f"Ok{_i}/5", f"Bad{_i}/4"]

FOX = (
    "invocabulary { " + " ".join(_IN) + " }\n"
    "outvocabulary { " + " ".join(_OUT) + " }\n"
    "theory {\n" + _theory() + "\n}\n"
)
FLAGS = []


def structure(instance):
    s = {
        "domain": range(max(TOP, BASE - 1) + 1),
        "Val": range(1, TOP + 1),
        "Dig": range(BASE),
        "Dpos": range(NDIG),
        "Cpos": range(NDIG + 1),
        "Nxt": [(q, q + 1) for q in range(NDIG)],
        "Zero": [0],
        "Last": [NDIG],
        "Bit": [0, 1],
        "DigOf": [(v, q, _digit(v, q)) for v in range(1, TOP + 1) for q in range(NDIG)],
    }
    for p in PEOPLE:
        s[f"Cap_{p}"] = range(1, CAP[p] + 1)
    for i, (_, _, c) in enumerate(PAIRS):
        ok, bad = [], []
        for q in range(NDIG):
            t = _digit(c, q)
            for x in range(BASE):
                for y in range(BASE):
                    for k in (0, 1):
                        total = x + y + k
                        if total % BASE == t:
                            ok.append((q, x, y, k, total // BASE))
                        else:
                            bad.append((q, x, y, k))
        s[f"Ok{i}"] = ok
        s[f"Bad{i}"] = bad
    return s
