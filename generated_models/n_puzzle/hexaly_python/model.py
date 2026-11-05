"""N-puzzle: slide tiles into the empty square, one move per step, from the start state to the end state
in exactly N_STEPS states.

The grid holds tiles and one empty square (0). A move slides a neighbouring tile into the empty
square, and the state must change at every step.
"""
import hexaly.optimizer as hx


def build(instance):
    # N_STEPS: number of states in the trace, start and end included (so N_STEPS - 1 moves)
    # puzzle_start, puzzle_end: square grids of tile numbers, 0 marks the empty square
    steps, start, end = instance["N_STEPS"], instance["puzzle_start"], instance["puzzle_end"]
    size = len(start)  # side of the grid
    cells = size * size
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # blank[t] is the square (r * size + c) of the empty tile in state t. Each state follows from the
    # previous one and the next blank square, so the blank squares are the only decisions.
    # blank[0] is fixed by the start state; the other N_STEPS - 1 are decision variables over all squares.
    first = [v for row in start for v in row]
    blank = [first.index(0)] + [model.int(0, cells - 1) for _ in range(steps - 1)]

    # The empty tile moves to a horizontally or vertically adjacent square at every step, so the
    # state always changes (a tile and the empty square swap, and the two differ)
    for t in range(steps - 1):
        a, b = blank[t], blank[t + 1]
        model.constraint(model.abs(a // size - b // size) + model.abs(a % size - b % size) == 1)

    # State t + 1: the tile on the new blank square slides into the old one; the others stay
    # (states[t][k] is the tile on square k in state t, as a Hexaly expression built from the blank squares)
    states = [first]
    for t in range(steps - 1):
        previous = model.array(states[-1])
        moved = model.at(previous, blank[t + 1])
        states.append([model.iif(blank[t] == k, moved, model.iif(blank[t + 1] == k, 0, states[-1][k]))
                       for k in range(cells)])

    # The last state is the end state
    goal = [v for row in end for v in row]
    for k in range(cells):
        model.constraint(states[-1][k] == goal[k])

    # steps[t][r][c] is the tile at row r, column c in state t, the layout the output requires
    grid = [[[state[r * size + c] for c in range(size)] for r in range(size)] for state in states]
    return optimizer, {"steps": grid}
