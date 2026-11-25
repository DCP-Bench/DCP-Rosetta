# csplib_009_perfect_square_placement: a FOX model for GroundFOX from DCP Rosetta.
#
# The perfect square placement problem (also called the squared square problem) is to pack a
# set of squares with given integer sizes into a bigger square in such a way that no squares
# overlap each other and all square borders are parallel to the border of the big square. The
# sum of the square surfaces is equal to the surface of the packing square, so that there is
# no spare capacity. A simple perfect square placement problem is a perfect square placement
# problem in which no subset of the squares (greater than one) are placed in a rectangle.
#
# Print the coordinates of the squares (x_coords, y_coords) as lists of integers - starting
# from 0.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_009_perfect_square_placement.json --check

# csplib_009_perfect_square_placement: a FOX model for GroundFOX from DCP Rosetta.
#
# Pack squares of the given sides into a base x base square with no overlaps and all borders
# parallel to the big square's border. Print the coordinates (x_coords, y_coords) from 0.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# Every square gets one x and one y coordinate, inside the base (Inside is data: the square fits).
# Every pair of squares is separated in x or in y: xlt(i,j) says i lies left of j, ylt(i,j) says
# i lies below j. If i is left of j, j starts at or after i's end: Fit(i, a, b) is the data relation
# b >= a + side(i). A square with no fitting b for its coordinate a cannot be left of anything.
# The one-value-per-square condition uses a ladder (seen) instead of pairwise clauses.
FOX = """
invocabulary { Sq/1 Coord/1 Pair/2 Next/2 Fit/3 Inside/2 }
outvocabulary { x_coords/2 y_coords/2 xlt/2 ylt/2 seenx/2 seeny/2 }
theory {
    ! i [Sq(i)] : ? a [Coord(a)] : x_coords(i,a).
    ! i [Sq(i)] : ? a [Coord(a)] : y_coords(i,a).

    ! i [Sq(i)] : ! a [Coord(a)] : ~x_coords(i,a) | seenx(i,a).
    ! i [Sq(i)] : ! a [Coord(a)] : ~y_coords(i,a) | seeny(i,a).
    ! i [Sq(i)] : ! a [Coord(a)] : ! b [Next(a,b)] : ~seenx(i,a) | seenx(i,b).
    ! i [Sq(i)] : ! a [Coord(a)] : ! b [Next(a,b)] : ~seeny(i,a) | seeny(i,b).
    ! i [Sq(i)] : ! a [Coord(a)] : ! b [Next(a,b)] : ~seenx(i,a) | ~x_coords(i,b).
    ! i [Sq(i)] : ! a [Coord(a)] : ! b [Next(a,b)] : ~seeny(i,a) | ~y_coords(i,b).

    ! i [Sq(i)] : ! a [Coord(a) & ~Inside(i,a)] : ~x_coords(i,a).
    ! i [Sq(i)] : ! a [Coord(a) & ~Inside(i,a)] : ~y_coords(i,a).

    ! i [Sq(i)] : ! j [Pair(i,j)] : xlt(i,j) | xlt(j,i) | ylt(i,j) | ylt(j,i).

    ! i [Sq(i)] : ! j [Sq(j) & i ~= j] : ! a [Coord(a) & ~? b : Fit(i,a,b)] : ~xlt(i,j) | ~x_coords(i,a).
    ! i [Sq(i)] : ! j [Sq(j) & i ~= j] : ! a [Coord(a) & ? b : Fit(i,a,b)] : ? b [Fit(i,a,b)] : x_coords(j,b) | ~xlt(i,j) | ~x_coords(i,a).
    ! i [Sq(i)] : ! j [Sq(j) & i ~= j] : ! a [Coord(a) & ~? b : Fit(i,a,b)] : ~ylt(i,j) | ~y_coords(i,a).
    ! i [Sq(i)] : ! j [Sq(j) & i ~= j] : ! a [Coord(a) & ? b : Fit(i,a,b)] : ? b [Fit(i,a,b)] : y_coords(j,b) | ~ylt(i,j) | ~y_coords(i,a).
}
"""


def structure(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)
    coords = list(range(base))
    squares = list(range(n))
    return {
        "domain": coords + squares,
        "Sq": squares,
        "Coord": coords,
        "Pair": [(i, j) for i in squares for j in squares if i < j],
        "Next": [(a, a + 1) for a in range(base - 1)],
        "Fit": [(i, a, b) for i in squares for a in coords for b in coords if a + sides[i] <= b],
        "Inside": [(i, a) for i in squares for a in coords if a + sides[i] <= base],
    }
