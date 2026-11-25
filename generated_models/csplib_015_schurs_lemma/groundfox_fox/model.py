# csplib_015_schurs_lemma: a FOX model for GroundFOX from DCP Rosetta.
#
# The problem is to put \( n \) balls labelled \( 1, \ldots, n \) into 3 boxes so that for any
# triple of balls \( (x, y, z) \) with \( x + y = z \), where \( x \) and \( y \) may be
# equal, not all are in the same box. This has a solution iff \( n < 14 \). The problem can be
# formulated as a 0-1 problem using the variables \( M_{ij} \) for \( i \in \{1, \ldots, n\},
# j \in \{1, 2, 3\} \) with \( M_{ij} \) true if ball \( i \) is in box \( j \). The
# constraints are that a ball must be in exactly one box, \( M_{i1} + M_{i2} + M_{i3} = 1 \)
# for all \( i \in \{1, \ldots, n\} \). And for each \( x + y = z \) and \( j \in \{1, 2, 3\}
# \), not \( (M_{xj} \land M_{yj} \land M_{zj}) \). This converts to, \( (1 - M_{xj}) + (1 -
# M_{yj}) + (1 - M_{zj}) \geq 1 \) or, \( M_{xj} + M_{yj} + M_{zj} \leq 2 \).
#
# Print the assignment of balls to boxes (balls) as a list of n integers from 1 to 3.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_015_schurs_lemma.json --check

# csplib_015_schurs_lemma: a FOX model for GroundFOX from DCP Rosetta.
#
# Put the balls 1..n into boxes so that for every triple of balls (x, y, z) with x + y = z
# (x and y may be equal), not all three are in the same box. Print the box of each ball.
#
# Balls are indexed 0..n-1 (ball label = index + 1); boxes are 1..c. The triples are data
# computed from n in structure(); the theory only forbids a monochromatic triple.

def _theory():
    return (
        "invocabulary { Ball/1 Box/1 Tri/3 }\n"
        "outvocabulary { balls/2 }\n"
        "theory {\n"
        "    ! x [Ball(x)] : ? j [Box(j)] : balls(x, j).\n"
        "    ! x [Ball(x)] : ! j [Box(j)] : ! k [Box(k) & j ~= k] : ~balls(x, j) | ~balls(x, k).\n"
        "    ! x [Ball(x)] : ! y [Ball(y)] : ! z [Tri(x, y, z)] : ! j [Box(j)] : "
        "~balls(x, j) | ~balls(y, j) | ~balls(z, j).\n"
        "}\n"
    )


FOX = _theory()


def structure(instance):
    n = instance["n"]
    c = instance["c"]
    # labels x+1, y+1 with (x+1)+(y+1) = z+1, i.e. z = x + y + 1 on indices
    tri = [(x, y, x + y + 1) for x in range(n) for y in range(n) if x + y + 1 < n]
    return {
        "domain": range(0, max(n, c + 1)),
        "Ball": range(n),
        "Box": range(1, c + 1),
        "Tri": tri,
    }
