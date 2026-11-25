# kakuro: a FOX model for GroundFOX from DCP Rosetta.
#
# The object of the puzzle is to insert a digit from 1 to 9 inclusive into each white cell
# such that the sum of the numbers in each entry matches the clue associated with it and that
# no digit is duplicated in any entry. It is that lack of duplication that makes creating
# Kakuro puzzles with unique solutions possible, and which means solving a Kakuro puzzle
# involves investigating combinations more, compared to Sudoku in which the focus is on
# permutations. There is an unwritten rule for making Kakuro puzzles that each clue must have
# at least two numbers that add up to it. This is because including one number is
# mathematically trivial when solving Kakuro puzzles; one can simply disregard the number
# entirely and subtract it from the clue it indicates.
#
# Print the solution matrix (x) as a list of lists of integers ranging from 0 to 9; 0
# represents a blank cell.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py kakuro.json --check

# kakuro: a FOX model for GroundFOX from DCP Rosetta.
#
# Kakuro on an n x n grid: fill every white cell with a digit 1..9 so that each clue run (a sequence
# of white cells with its clue sum) adds up to the clue and uses no digit twice. Print the solution
# matrix (x) with 0 for black cells.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Coord/1 Wht/2 Blk/2 Dig/1 Dig0/1 Sum/1 SNext/2 Add/3 Pos/1 First/1 Last/1 Nxt/2 CellOf/3 Peer/4 TgtAt/2 }
outvocabulary { x/3 St/2 Seen/2 }
theory {
    ! r [Coord(r)] : ! c [Blk(r,c)] : x(r,c,0).
    ! r [Coord(r)] : ! c [Wht(r,c)] : ~x(r,c,0).
    ! r [Coord(r)] : ! c [Wht(r,c)] : ? v [Dig(v)] : x(r,c,v).
    ! r [Coord(r)] : ! c [Coord(c)] : ! v [Dig0(v)] : ! w [Dig0(w) & ~(v = w)] : ~x(r,c,v) | ~x(r,c,w).
    ! r1 [Coord(r1)] : ! c1 [Coord(c1)] : ! r2 [Coord(r2)] : ! c2 [Peer(r1,c1,r2,c2)] : ! v [Dig(v)] : ~x(r1,c1,v) | ~x(r2,c2,v).
    ! q [Pos(q)] : ? s [Sum(s)] : St(q,s).
    ! q [Pos(q)] : ! s [Sum(s)] : ~St(q,s) | Seen(q,s).
    ! q [Pos(q)] : ! s [Sum(s)] : ! t [SNext(s,t)] : ~Seen(q,s) | Seen(q,t).
    ! q [Pos(q)] : ! s [Sum(s)] : ! t [SNext(s,t)] : ~Seen(q,s) | ~St(q,t).
    ! q [First(q)] : ! r [Coord(r)] : ! c [CellOf(q,r,c)] : ! v [Dig(v)] : ~x(r,c,v) | St(q,v).
    ! p [Pos(p)] : ! q [Nxt(p,q)] : ! r [Coord(r)] : ! c [CellOf(q,r,c)] : ! s [Sum(s)] : ! v [Dig(v)] : ! t [Add(s,v,t)] : ~St(p,s) | ~x(r,c,v) | St(q,t).
    ! q [Last(q)] : ! s [Sum(s) & ~TgtAt(q,s)] : ~St(q,s).
}
"""


def _runs(instance):
    # Each clue segment is [sum, [r, c], [r, c], ...]: the sum first, then its cells.
    return [(int(seg[0]), [tuple(int(v) for v in cell) for cell in seg[1:]]) for seg in instance["problem"]]


def structure(instance):
    n = int(instance["n"])
    runs = _runs(instance)
    blanks = [tuple(int(v) for v in p) for p in instance["blanks"]]
    # Coordinates are 1-based when none is 0; shift them to 0-based.
    coords = [v for p in blanks for v in p] + [v for _, cells in runs for p in cells for v in p]
    shift = 1 if coords and min(coords) >= 1 else 0
    # The "blanks" are the black cells (clue cells and padding); every other cell is white.
    black = {(r - shift, c - shift) for r, c in blanks}
    runs = [(total, [(r - shift, c - shift) for r, c in cells]) for total, cells in runs]

    grid = [(r, c) for r in range(n) for c in range(n)]
    white = [p for p in grid if p not in black]
    black = sorted(black)

    cell_of, nxt, first, last, tgt, peer = [], [], [], [], [], set()
    for total, cells in runs:
        ids = []
        for cell in cells:
            ids.append(len(cell_of))
            cell_of.append(cell)
        first.append(ids[0])
        last.append(ids[-1])
        tgt.append((ids[-1], total))
        nxt.extend(zip(ids, ids[1:]))
        for a in cells:
            for b in cells:
                if a != b:
                    peer.add(a + b)

    sums = list(range(0, 46))
    add = [(s, v, s + v) for s in sums for v in range(1, 10) if s + v <= 45]
    snext = list(zip(sums, sums[1:]))
    return {
        "Coord": list(range(n)),
        "Wht": sorted(white),
        "Blk": black,
        "Dig": list(range(1, 10)),
        "Dig0": list(range(0, 10)),
        "Sum": sums,
        "SNext": snext,
        "Add": add,
        "Pos": list(range(len(cell_of))),
        "First": first,
        "Last": last,
        "Nxt": nxt,
        "CellOf": [(q, r, c) for q, (r, c) in enumerate(cell_of)],
        "Peer": sorted(peer),
        "TgtAt": tgt,
    }
