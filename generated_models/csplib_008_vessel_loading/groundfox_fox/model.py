# csplib_008_vessel_loading: a FOX model for GroundFOX from DCP Rosetta.
#
# Supply vessels transport containers from site to site. The deck area is rectangular.
# Containers are cuboid, and are laid out in a single layer. All containers are positioned
# parallel to the sides of the deck. The contents of the containers determine their class.
# Certain classes of containers are constrained to be separated by minimum distances either
# along the deck or across the deck.
#
# A container occupies the area from `left` to `right` across the width of the deck, and from
# `bottom` to `top` along its length, with `right - left` and `top - bottom` being its width
# and length, in that order or rotated by 90 degrees. All of these lie between 0 and the
# deck's size in that direction. Two containers may touch. `separation[a-1][b-1]` is the
# distance that containers of classes `a` and `b` must keep in at least one of the two
# directions.
#
# The vessel loading decision problem is to determine whether a given set of containers can be
# positioned on a given deck, without overlapping, and without violating any of the separation
# constraints.
#
# Print the positions of the containers (left, right, top, bottom), as lists of integers -
# starting from 0.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_008_vessel_loading.json --check

# csplib_008_vessel_loading: a FOX model for GroundFOX from DCP Rosetta.
#
# Place the containers (n_containers of them) on a rectangular deck without overlap, with
# minimum separations between classes in at least one of the two directions. Each container is
# either width-along-x or length-along-x (rot 0 / rot 1).
# Outputs: left, right (x-extent), bottom, top (y-extent) per container, 0-based.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Cont/1 Pair/2 Xc/1 Yc/1 G/4 DX0/3 DX1/3 DY0/3 DY1/3 }
outvocabulary { left/2 right/2 bottom/2 top/2 rot/2 dir/3 }
theory {
    ! i [Cont(i)] : ? l [Xc(l)] : left(i,l).
    ! i [Cont(i)] : ! l [Xc(l)] : ! m [Xc(m) & l ~= m] : ~left(i,l) | ~left(i,m).
    ! i [Cont(i)] : ? r [Xc(r)] : right(i,r).
    ! i [Cont(i)] : ! l [Xc(l)] : ! m [Xc(m) & l ~= m] : ~right(i,l) | ~right(i,m).
    ! i [Cont(i)] : ? b [Yc(b)] : bottom(i,b).
    ! i [Cont(i)] : ! l [Yc(l)] : ! m [Yc(m) & l ~= m] : ~bottom(i,l) | ~bottom(i,m).
    ! i [Cont(i)] : ? t [Yc(t)] : top(i,t).
    ! i [Cont(i)] : ! l [Yc(l)] : ! m [Yc(m) & l ~= m] : ~top(i,l) | ~top(i,m).
    ! i [Cont(i)] : rot(i,0) | rot(i,1).
    ! i [Cont(i)] : ~rot(i,0) | ~rot(i,1).
    ! i [Cont(i)] : ! l [Xc(l)] : ! r [Xc(r) & ~DX0(i,l,r)] : ~rot(i,0) | ~left(i,l) | ~right(i,r).
    ! i [Cont(i)] : ! l [Xc(l)] : ! r [Xc(r) & ~DX1(i,l,r)] : ~rot(i,1) | ~left(i,l) | ~right(i,r).
    ! i [Cont(i)] : ! b [Yc(b)] : ! t [Yc(t) & ~DY0(i,b,t)] : ~rot(i,0) | ~bottom(i,b) | ~top(i,t).
    ! i [Cont(i)] : ! b [Yc(b)] : ! t [Yc(t) & ~DY1(i,b,t)] : ~rot(i,1) | ~bottom(i,b) | ~top(i,t).
    ! i [Cont(i)] : ! j [Pair(i,j)] : dir(i,j,0) | dir(i,j,1) | dir(i,j,2) | dir(i,j,3).
    ! i [Cont(i)] : ! j [Pair(i,j)] : ! x [Xc(x)] : ! y [Xc(y) & ~G(i,j,x,y)] : ~dir(i,j,0) | ~right(i,x) | ~left(j,y).
    ! i [Cont(i)] : ! j [Pair(i,j)] : ! x [Xc(x)] : ! y [Xc(y) & ~G(i,j,x,y)] : ~dir(i,j,1) | ~right(j,x) | ~left(i,y).
    ! i [Cont(i)] : ! j [Pair(i,j)] : ! x [Yc(x)] : ! y [Yc(y) & ~G(i,j,x,y)] : ~dir(i,j,2) | ~top(i,x) | ~bottom(j,y).
    ! i [Cont(i)] : ! j [Pair(i,j)] : ! x [Yc(x)] : ! y [Yc(y) & ~G(i,j,x,y)] : ~dir(i,j,3) | ~top(j,x) | ~bottom(i,y).
}
"""


def structure(instance):
    W = instance["deck_width"]
    L = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]
    length = instance["length"]
    classes = instance["classes"]
    sep = instance["separation"]
    M = max(W, L, 1)
    coords = range(M + 1)
    conts = range(n)
    pairs = [(i, j) for i in conts for j in conts if i < j]
    gap = []
    for i, j in pairs:
        d = sep[classes[i] - 1][classes[j] - 1]
        gap.extend((i, j, x, y) for x in coords for y in coords if y >= x + d)
    # rot 0: x-extent is the width, y-extent the length; rot 1: swapped.
    return {
        "domain": list(coords),
        "Cont": list(conts),
        "Pair": pairs,
        "Xc": list(range(W + 1)),
        "Yc": list(range(L + 1)),
        "G": gap,
        "DX0": [(i, l, r) for i in conts for l in coords for r in coords if r - l == width[i]],
        "DX1": [(i, l, r) for i in conts for l in coords for r in coords if r - l == length[i]],
        "DY0": [(i, b, t) for i in conts for b in coords for t in coords if t - b == length[i]],
        "DY1": [(i, b, t) for i in conts for b in coords for t in coords if t - b == width[i]],
    }
