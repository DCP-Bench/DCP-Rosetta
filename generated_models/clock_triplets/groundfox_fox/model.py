# clock_triplets: a FOX model for GroundFOX from DCP Rosetta.
#
# Rearrange the numbers on the face of a clock (1 to 12) so no triplet of adjacent numbers has
# a sum higher than 21. This is the smallest value that the highest sum of a triplet can have.
#
# Print the arrangement of the numbers on the clock (x) as a list of 12 integers - ranging
# from 1 to 12.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py clock_triplets.json --check

# clock_triplets: a GroundFOX model. Position i (0-based, clockwise) holds the value x(i, v) in 1..12.
# Each triplet of cyclically adjacent positions must sum to at most 21.

FACE = 12
LIMIT = 21

_triples = [(p, (p + 1) % FACE, (p + 2) % FACE) for p in range(FACE)]

_lines = []
for (p, q, r) in _triples:
    _lines.append("    ! a : ! b : ! c [Bad(a, b, c)] : ~x(%d, a) | ~x(%d, b) | ~x(%d, c)." % (p, q, r))

FOX = """
invocabulary { Pos/1 Val/1 Bad/3 }
outvocabulary { x/2 }
theory {
    ! i [Pos(i)] : ? v [Val(v)] : x(i, v).
    ! i [Pos(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(i, v) | ~x(i, w).
    ! v [Val(v)] : ! i [Pos(i)] : ! j [Pos(j) & i ~= j] : ~x(i, v) | ~x(j, v).
%s
}
""" % "\n".join(_lines)


def structure(instance):
    vals = range(1, FACE + 1)
    bad = [(a, b, c) for a in vals for b in vals for c in vals if a + b + c > LIMIT]
    return {"Pos": range(FACE), "Val": vals, "Bad": bad}
