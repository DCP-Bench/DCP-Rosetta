# eighteen_hole_golf: a FOX model for GroundFOX from DCP Rosetta.
#
# Generate an 18-hole golf course where each hole has a length of 3, 4, or 5, and the total
# length of the course is 72.
#
# Print the lengths of the holes (holes) as a list of 18 integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py eighteen_hole_golf.json --check

# eighteen_hole_golf: a FOX model for GroundFOX from DCP Rosetta.
#
# Generate an 18-hole golf course where each hole has a length of 3, 4 or 5 and the total
# length of the course is 72. Print the lengths of the holes (holes) as 18 integers.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# A layered chain of partial sums Ch(j, s): after the first j holes the length is s. Each
# hole chooses one length; the chain is walked backwards from the final total.
FOX = """
invocabulary { Hole/1 Len/1 Nx/2 Sb/3 Lay/1 Zero/1 State/1 Bad/1 Last/1 Target/1 }
outvocabulary { holes/2 Ch/2 }
theory {
    ! i [Hole(i)] : ? c [Len(c)] : holes(i,c).
    ! i [Hole(i)] : ! c [Len(c)] : ! d [Len(d) & c ~= d] : ~holes(i,c) | ~holes(i,d).

    ! y [Zero(y)] : Ch(0,y).
    ! y [State(y) & ~Zero(y)] : ~Ch(0,y).
    ! j [Lay(j)] : ! y [Bad(y)] : ~Ch(j,y).
    ! i [Hole(i)] : ! j [Nx(i,j)] : ! y [State(y)] : ! c [Len(c)] : ! x [Sb(y,c,x)] : ~Ch(j,y) | ~holes(i,c) | Ch(i,x).
    ! j [Last(j)] : ! y [State(y) & ~Target(y)] : ~Ch(j,y).
    ! j [Last(j)] : ? y [Target(y)] : Ch(j,y).
}
"""


def structure(instance):
    lengths = [3, 4, 5]
    holes = list(range(18))
    total = 72
    top = 18 * max(lengths)            # largest possible partial sum
    bad = top + 1                      # sentinel: a sum that would be negative
    states = list(range(top + 1))
    sb = []
    for y in states:
        for c in lengths:
            x = y - c
            sb.append((y, c, x if x >= 0 else bad))
    return {
        "domain": list(range(bad + 1)),
        "Hole": holes,
        "Len": lengths,
        "Nx": [(i, i + 1) for i in holes],
        "Sb": sb,
        "Lay": list(range(len(holes) + 1)),
        "Zero": [0],
        "State": states + [bad],
        "Bad": [bad],
        "Last": [len(holes)],
        "Target": [total],
    }
