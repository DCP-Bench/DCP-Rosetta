# session1_five_floors: a FOX model for GroundFOX from DCP Rosetta.
#
# Baker, Cooper, Fletcher, Miller, and Smith live on the first five floors of an apartment
# house. Baker does not live on the fifth floor. Cooper does not live on the first floor.
# Fletcher does not live on either the fifth or the first floor. Miller lives on a higher
# floor than does Cooper. Smith does not live on a floor adjacent to Fletcher’s. Fletcher does
# not live on a floor adjacent to Cooper’s. They all live on different floors. Find the floors
# where these people live.
#
# Print the floors where each person lives (B, C, F, M, S).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session1_five_floors.json --check

# session1_five_floors: a FOX model for GroundFOX from DCP Rosetta.
#
# Five people (Baker, Cooper, Fletcher, Miller, Smith) on floors 1..5, all different, with the
# adjacency and ordering conditions of the puzzle. Outputs B, C, F, M, S are the floors.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Floor/1 Adj/2 Gt/2 }
outvocabulary { B/1 C/1 F/1 M/1 S/1 }
theory {
    ? v [Floor(v)] : B(v).
    ? v [Floor(v)] : C(v).
    ? v [Floor(v)] : F(v).
    ? v [Floor(v)] : M(v).
    ? v [Floor(v)] : S(v).
    ! v [Floor(v)] : ! w [Floor(w) & v ~= w] : ~B(v) | ~B(w).
    ! v [Floor(v)] : ! w [Floor(w) & v ~= w] : ~C(v) | ~C(w).
    ! v [Floor(v)] : ! w [Floor(w) & v ~= w] : ~F(v) | ~F(w).
    ! v [Floor(v)] : ! w [Floor(w) & v ~= w] : ~M(v) | ~M(w).
    ! v [Floor(v)] : ! w [Floor(w) & v ~= w] : ~S(v) | ~S(w).
    ! v [Floor(v)] : ~B(v) | ~C(v).
    ! v [Floor(v)] : ~B(v) | ~F(v).
    ! v [Floor(v)] : ~B(v) | ~M(v).
    ! v [Floor(v)] : ~B(v) | ~S(v).
    ! v [Floor(v)] : ~C(v) | ~F(v).
    ! v [Floor(v)] : ~C(v) | ~M(v).
    ! v [Floor(v)] : ~C(v) | ~S(v).
    ! v [Floor(v)] : ~F(v) | ~M(v).
    ! v [Floor(v)] : ~F(v) | ~S(v).
    ! v [Floor(v)] : ~M(v) | ~S(v).
    ! u [u = 5] : ~B(5).
    ! u [u = 1] : ~C(1).
    ! u [u = 1] : ~F(1).
    ! u [u = 5] : ~F(5).
    ! v [Floor(v)] : ! w [Adj(v,w)] : ~S(v) | ~F(w).
    ! v [Floor(v)] : ! w [Adj(v,w)] : ~F(v) | ~C(w).
    ! v [Floor(v)] : ! w [Floor(w) & ~Gt(v,w)] : ~M(v) | ~C(w).
}
"""


def structure(instance):
    floors = [1, 2, 3, 4, 5]
    return {
        "domain": floors,
        "Floor": floors,
        "Adj": [(v, w) for v in floors for w in floors if abs(v - w) == 1],
        "Gt": [(v, w) for v in floors for w in floors if v > w],
    }
