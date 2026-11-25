# bowls_and_oranges: a FOX model for GroundFOX from DCP Rosetta.
#
# You have a number of bowls, numbered from 1 and all placed in a line at exact intervals of 1
# meter. You also have a number of oranges. You wish to place all the oranges in the bowls, no
# more than one orange in each bowl, so that there are no three oranges A, B, and C such that
# the distance between A and B is equal to the distance between B and C.
#
# Print a solution to the problem as a list of numbers -in ascending order- representing the
# bowls in which the oranges are placed (x).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py bowls_and_oranges.json --check

# bowls_and_oranges: a FOX model for GroundFOX from DCP Rosetta.
#
# Place n oranges in m bowls numbered 1..m on a line, at most one orange per bowl,
# so that no three oranges A, B, C have dist(A,B) = dist(B,C). Output the bowl
# numbers of the oranges in ascending order (x).

FOX = """
invocabulary { Idx/1 Bowl/1 Lt/2 Leq/2 AP/3 }
outvocabulary { x/2 U/1 }
theory {
    ! i [Idx(i)] : ? v [Bowl(v)] : x(i, v).
    ! i [Idx(i)] : ! v [Bowl(v)] : ! w [Bowl(w) & v ~= w] : ~x(i, v) | ~x(i, w).
    ! i [Idx(i)] : ! j [Lt(i, j)] : ! v [Bowl(v)] : ! w [Leq(w, v)] : ~x(i, v) | ~x(j, w).
    ! v [Bowl(v)] : ! i [Idx(i)] : ~x(i, v) | U(v).
    ! a [Bowl(a)] : ! b [Bowl(b)] : ! c [AP(a, b, c)] : ~U(a) | ~U(b) | ~U(c).
}
"""


def structure(instance):
    m = instance["n"]
    n = instance["m"]
    bowls = list(range(1, m + 1))
    return {
        "domain": range(0, max(n, m) + 2),
        "Idx": range(n),
        "Bowl": bowls,
        "Lt": [(i, j) for i in range(n) for j in range(i + 1, n)],
        "Leq": [(w, v) for v in bowls for w in bowls if w <= v],
        # a < b < c with b - a = c - b
        "AP": [(a, (a + c) // 2, c) for a in bowls for c in bowls if a < c and (a + c) % 2 == 0],
    }
