# curious_set_of_integers: a FOX model for GroundFOX from DCP Rosetta.
#
# The integers 1,3,8, and 120 form a set with a remarkable property: the product of any two
# integers is one less than a perfect square. Find a fifth number (larger than or equal to 0)
# that can be added to the set without destroying this property.
#
# Print this number (number).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py curious_set_of_integers.json --check

# curious_set_of_integers: a FOX model for GroundFOX from DCP Rosetta.
#
# number is a value 0..max_val such that a * number + 1 is a perfect square for every
# element a of the given set. The allowed pairs (a, x) are data computed in structure.
# "Exactly one value" is a linear prefix chain (seen(x): a number occurs at or before x)
# rather than a pairwise at-most-one, which is quadratic in max_val.

import math

FOX = """
invocabulary { Val/1 Elem/1 Ok/2 Next/2 }
outvocabulary { number/1 seen/1 }
theory {
    ? x [Val(x)] : number(x).
    ! x [Val(x)] : ! a [Elem(a) & ~Ok(a, x)] : ~number(x).
    ! x [Val(x)] : ~number(x) | seen(x).
    ! x [Val(x)] : ! y [Next(x, y)] : ~seen(x) | seen(y).
    ! x [Val(x)] : ! y [Next(x, y)] : ~seen(x) | ~number(y).
}
"""

ELEMENTS = [1, 3, 8, 120]


def structure(instance):
    max_val = instance["max_val"]
    ok = []
    for a in ELEMENTS:
        for x in range(max_val + 1):
            r = a * x + 1
            if math.isqrt(r) ** 2 == r:
                ok.append((a, x))
    return {
        "Val": list(range(max_val + 1)),
        "Elem": ELEMENTS,
        "Ok": ok,
        "Next": [(x, x + 1) for x in range(max_val)],
    }
