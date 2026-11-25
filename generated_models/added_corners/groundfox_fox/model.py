# added_corners: a FOX model for GroundFOX from DCP Rosetta.
#
# Enter the digits 1 through 8 into the eight positions around the edge of a 3 by 3 grid whose
# centre is empty, using each digit exactly once. The corners are circles (C) and the middles
# of the sides are squares (F):
#
# ```text C F C F F C F C ```
#
# The number in each square must equal the sum of the numbers in the two circles adjoining it.
#
# Print the values for each position (positions), starting from the top left corner and moving
# like reading a book, i.e., left to right, top to bottom.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py added_corners.json --check

FOX = """
invocabulary { Pos/1 Val/1 Sq/3 Add/3 }
outvocabulary { positions/2 }
theory {
    ! i [Pos(i)] : ? v [Val(v)] : positions(i, v).
    ! i [Pos(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~positions(i, v) | ~positions(i, w).
    ! v [Val(v)] : ? i [Pos(i)] : positions(i, v).
    ! v [Val(v)] : ! i [Pos(i)] : ! j [Pos(j) & i ~= j] : ~positions(i, v) | ~positions(j, v).
    ! s [Pos(s)] : ! c1 [Pos(c1)] : ! c2 [Sq(s, c1, c2)] : ! a [Val(a)] : ! b [Val(b)] : ! c [Val(c) & ~Add(a, b, c)] : ~positions(c1, a) | ~positions(c2, b) | ~positions(s, c).
}
"""


def structure(instance):
    # Positions 0..7 read like a book: 0 TL, 1 TM, 2 TR, 3 ML, 4 MR, 5 BL, 6 BM, 7 BR.
    # Each square (1 TM, 3 ML, 4 MR, 6 BM) is the sum of its two adjoining circles.
    return {
        "Pos": range(8),
        "Val": range(1, 9),
        "Sq": [(1, 0, 2), (3, 0, 5), (4, 2, 7), (6, 5, 7)],
        "Add": [(a, b, a + b) for a in range(1, 9) for b in range(1, 9) if a + b <= 8],
    }
