# n_puzzle: a FOX model for GroundFOX from DCP Rosetta.
#
# The N-Puzzle is a classic sliding puzzle game where the goal is to move tiles on a grid to
# achieve a specific end configuration. The puzzle consists of a grid with \( n+1 \) tiles,
# one of which is empty. The objective is to trace the steps to the original picture by moving
# the tiles into their correct positions.
#
# Input includes the start and end state of the puzzle, in which 0 is the empty tile, along
# with the number of steps to the solution, which includes the start and end states. Each step
# moves one tile that is horizontally or vertically next to the empty tile into the empty
# position. Also, "freezing" is not allowed, meaning that the state of the puzzle must change
# at each step.
#
# Print the state of the puzzle at each step (steps) as a list of exactly N_STEPS integer
# 2-dimensional matrices, including the start and end states.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py n_puzzle.json --check

FOX = """
invocabulary { Step/1 Last/1 Nxt/2 Row/1 Col/1 Val/1 Other/4 Edge/1 Mv/5 Init/3 Goal/3 }
outvocabulary { steps/4 M/2 }
theory {
    ! r [Row(r)] : ! c [Col(c)] : ! v [Init(r, c, v)] : steps(0, r, c, v).
    ! l [Last(l)] : ! r [Row(r)] : ! c [Col(c)] : ! v [Goal(r, c, v)] : steps(l, r, c, v).

    ! s [Step(s)] : ! r [Row(r)] : ! c [Col(c)] : ? v [Val(v)] : steps(s, r, c, v).
    ! s [Step(s)] : ! r [Row(r)] : ! c [Col(c)] : ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~steps(s, r, c, v) | ~steps(s, r, c, w).
    ! s [Step(s)] : ! v [Val(v)] : ! r1 [Row(r1)] : ! c1 [Col(c1)] : ! r2 [Row(r2)] : ! c2 [Other(r1, c1, r2, c2)] : ~steps(s, r1, c1, v) | ~steps(s, r2, c2, v).

    ! s [Step(s) & ? t : Nxt(s, t)] : ? k [Edge(k)] : M(s, k).
    ! s [Step(s) & ? t : Nxt(s, t)] : ! k [Edge(k)] : ! k2 [Edge(k2) & ~(k = k2)] : ~M(s, k) | ~M(s, k2).
    ! s [Step(s) & ? t : Nxt(s, t)] : ! k [Edge(k)] : ! r1 [Row(r1)] : ! c1 [Col(c1)] : ! r2 [Row(r2)] : ! c2 [Mv(k, r1, c1, r2, c2)] : ~M(s, k) | steps(s, r1, c1, 0).
    ! s [Step(s)] : ! t [Nxt(s, t)] : ! k [Edge(k)] : ! r1 [Row(r1)] : ! c1 [Col(c1)] : ! r2 [Row(r2)] : ! c2 [Mv(k, r1, c1, r2, c2)] : ! v [Val(v)] : ~M(s, k) | ~steps(s, r2, c2, v) | steps(t, r1, c1, v).
    ! s [Step(s)] : ! t [Nxt(s, t)] : ! k [Edge(k)] : ! r1 [Row(r1)] : ! c1 [Col(c1)] : ! r2 [Row(r2)] : ! c2 [Mv(k, r1, c1, r2, c2)] : ~M(s, k) | steps(t, r2, c2, 0).
    ! s [Step(s)] : ! t [Nxt(s, t)] : ! k [Edge(k)] : ! r1 [Row(r1)] : ! c1 [Col(c1)] : ! r2 [Row(r2)] : ! c2 [Mv(k, r1, c1, r2, c2)] : ! r3 [Row(r3)] : ! c3 [Other(r1, c1, r3, c3) & Other(r2, c2, r3, c3)] : ! v [Val(v)] : ~M(s, k) | ~steps(s, r3, c3, v) | steps(t, r3, c3, v).
}
"""


def structure(instance):
    start, end = instance["puzzle_start"], instance["puzzle_end"]
    steps = instance["N_STEPS"]
    rows, cols = len(start), len(start[0])
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    # Directed moves: edge k goes from the blank cell (r1, c1) to the neighbour (r2, c2).
    moves = [(r1, c1, r2, c2) for (r1, c1) in cells for (r2, c2) in cells
             if abs(r1 - r2) + abs(c1 - c2) == 1]
    return {
        "Step": list(range(steps)),
        "Last": [steps - 1],
        "Nxt": [(s, s + 1) for s in range(steps - 1)],
        "Row": list(range(rows)),
        "Col": list(range(cols)),
        "Val": list(range(rows * cols)),
        "Other": [(r1, c1, r2, c2) for (r1, c1) in cells for (r2, c2) in cells if (r1, c1) != (r2, c2)],
        "Edge": list(range(len(moves))),
        "Mv": [(k, r1, c1, r2, c2) for k, (r1, c1, r2, c2) in enumerate(moves)],
        "Init": [(r, c, start[r][c]) for (r, c) in cells],
        "Goal": [(r, c, end[r][c]) for (r, c) in cells],
    }
