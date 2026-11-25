# four_islands: a FOX model for GroundFOX from DCP Rosetta.
#
# A tiny nation in the South Pacific contains four islands connected by bridges as shown (see
# below). Each of the four islands (Pwana, Quero, Rayou, and Skern) boasts a different primary
# export (alabaster, bananas, coconuts, and durian fruit) and a different tourist attraction
# (hotel, ice skating rink, jai alai stadium, and koala preserve). Can you find the name,
# export, and tourist attraction of each island on the map?
#
# A, B, C, D are the islands, this is the map showing the bridges and the orientation of the
# islands:
#
# ```text (A) -- (B) | | | | (C) -- (D) ```
#
# This means that A is north of C, C is west of D, etc.
#
# 1. The island noted for its koala preserve is due south of Pwana. 2. The island with the
# largest alabaster quarry is due west of Quero. 3. The island with the resort hotel is due
# east of the one that exports durian fruit. 4. Skern and the island with the jai alai stadium
# are connected by a north-south bridge. 5. Rayou and the island that exports bananas are
# connected by an east-west bridge. 6. The islands noted for the South Pacific's largest ice
# skating rink and for the jai alai stadium are not connected by a bridge.
#
# Determine: Island name -- Export -- Tourist Attraction
#
# Print a number for each island (island), export (export), and attraction (attraction) as
# three lists of integers from 0 to 3. The value at each index is the map position of that
# item, encoded as A=0, B=1, C=2, D=3. The list indices refer respectively to: island =
# [Pwana, Quero, Rayou, Skern], export = [alabaster, bananas, coconuts, durian_fruit],
# attraction = [resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve].
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py four_islands.json --check

# four_islands: a GroundFOX model. Map positions A=0, B=1 (top row), C=2, D=3 (bottom row).
# island(k, p), export(e, p), attraction(t, p): entity k / export e / attraction t sits at map position p.
# Geometry on the 2x2 map is data: South(x, y) means x is due south of y, and so on.

FOX = """
invocabulary { Pos/1 Ent/1 South/2 West/2 East/2 NS/2 EW/2 Adj/2 }
outvocabulary { island/2 export/2 attraction/2 }
theory {
    ! k [Ent(k)] : ? p [Pos(p)] : island(k, p).
    ! k [Ent(k)] : ! p [Pos(p)] : ! q [Pos(q) & p ~= q] : ~island(k, p) | ~island(k, q).
    ! p [Pos(p)] : ! k [Ent(k)] : ! l [Ent(l) & k ~= l] : ~island(k, p) | ~island(l, p).

    ! k [Ent(k)] : ? p [Pos(p)] : export(k, p).
    ! k [Ent(k)] : ! p [Pos(p)] : ! q [Pos(q) & p ~= q] : ~export(k, p) | ~export(k, q).
    ! p [Pos(p)] : ! k [Ent(k)] : ! l [Ent(l) & k ~= l] : ~export(k, p) | ~export(l, p).

    ! k [Ent(k)] : ? p [Pos(p)] : attraction(k, p).
    ! k [Ent(k)] : ! p [Pos(p)] : ! q [Pos(q) & p ~= q] : ~attraction(k, p) | ~attraction(k, q).
    ! p [Pos(p)] : ! k [Ent(k)] : ! l [Ent(l) & k ~= l] : ~attraction(k, p) | ~attraction(l, p).

    ! p [Pos(p)] : ! q [Pos(q) & ~South(p, q)] : ~attraction(3, p) | ~island(0, q).
    ! p [Pos(p)] : ! q [Pos(q) & ~West(p, q)] : ~export(0, p) | ~island(1, q).
    ! h [Pos(h)] : ! d [Pos(d) & ~East(h, d)] : ~attraction(0, h) | ~export(3, d).
    ! s [Pos(s)] : ! j [Pos(j) & ~NS(s, j)] : ~island(3, s) | ~attraction(2, j).
    ! r [Pos(r)] : ! e [Pos(e) & ~EW(r, e)] : ~island(2, r) | ~export(1, e).
    ! i [Pos(i)] : ! j [Adj(i, j)] : ~attraction(1, i) | ~attraction(2, j).
}
"""


def structure(instance):
    return {
        "Pos": range(4),
        "Ent": range(4),
        "South": [(2, 0), (3, 1)],
        "West": [(0, 1), (2, 3)],
        "East": [(1, 0), (3, 2)],
        "NS": [(0, 2), (2, 0), (1, 3), (3, 1)],
        "EW": [(0, 1), (1, 0), (2, 3), (3, 2)],
        "Adj": [(0, 1), (1, 0), (2, 3), (3, 2), (0, 2), (2, 0), (1, 3), (3, 1)],
    }
