# circular_table_averbach_1_2: a FOX model for GroundFOX from DCP Rosetta.
#
# Three players (X, Y, Z) of different nationalities (American, English, French) are seated
# around a circular table playing a game of Hearts. Each passed three cards to the person on
# their right. Y passed three hearts to the American, X passed the queen of spades and two
# diamonds to the person who passed their cards to the Frenchwoman. Determine the nationality
# of each person.
#
# Print the values of X, Y, Z, American, English, French (x, y, z, american, english, french),
# such that the same value denotes the matching between the person and their nationality. Use
# 0, 1 or 2. Also, assume that 1 is right of 0, and 2 is right of 1 and so on.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py circular_table_averbach_1_2.json --check

# circular_table_averbach_1_2: a FOX model for GroundFOX from DCP Rosetta.
#
# Three players X, Y, Z of different nationalities (American, English, French) sit around a circular
# table; seat k is right of seat k-1 (seat 1 is right of 0, 2 is right of 1, and 0 is right of 2).
# Each passed three cards to the person on their right. Y passed to the American; X passed to the
# person who passed to the Frenchwoman. Print the seats of X, Y, Z and of the American, English,
# French (x, y, z, american, english, french).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Pos/1 Nxt/2 }
outvocabulary { x/1 y/1 z/1 american/1 english/1 french/1 }
theory {
    ? v [Pos(v)] : x(v).
    ! v [Pos(v)] : ! w [Pos(w) & ~(v = w)] : ~x(v) | ~x(w).
    ? v [Pos(v)] : y(v).
    ! v [Pos(v)] : ! w [Pos(w) & ~(v = w)] : ~y(v) | ~y(w).
    ? v [Pos(v)] : z(v).
    ! v [Pos(v)] : ! w [Pos(w) & ~(v = w)] : ~z(v) | ~z(w).
    ? v [Pos(v)] : american(v).
    ! v [Pos(v)] : ! w [Pos(w) & ~(v = w)] : ~american(v) | ~american(w).
    ? v [Pos(v)] : english(v).
    ! v [Pos(v)] : ! w [Pos(w) & ~(v = w)] : ~english(v) | ~english(w).
    ? v [Pos(v)] : french(v).
    ! v [Pos(v)] : ! w [Pos(w) & ~(v = w)] : ~french(v) | ~french(w).
    ! v [Pos(v)] : ~x(v) | ~y(v).
    ! v [Pos(v)] : ~x(v) | ~z(v).
    ! v [Pos(v)] : ~y(v) | ~z(v).
    ! v [Pos(v)] : ~american(v) | ~english(v).
    ! v [Pos(v)] : ~american(v) | ~french(v).
    ! v [Pos(v)] : ~english(v) | ~french(v).
    ! p [Pos(p)] : ! q [Nxt(p,q)] : ~y(p) | american(q).
    ! p [Pos(p)] : ! q [Nxt(p,q)] : ! r [Nxt(q,r)] : ~x(p) | french(r).
}
"""


def structure(instance):
    # Seats 0, 1, 2 around the table; each seat's right neighbour is the next seat (mod 3).
    return {"Pos": [0, 1, 2], "Nxt": [(0, 1), (1, 2), (2, 0)]}
