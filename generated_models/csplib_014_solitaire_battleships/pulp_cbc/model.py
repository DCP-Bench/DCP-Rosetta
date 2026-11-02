# csplib_014_solitaire_battleships: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

import pulp


def create_model(instance):
    """Solitaire battleships: fill a rows x cols grid with water and ship parts so that the
    fleet (ships of 1 to 4 squares in a straight line) is laid out with no two ships
    touching, even diagonally, the number of ship squares in every row and column is given,
    and the hinted cells are as shown."""
    rows = instance["rows"]        # the number of rows
    cols = instance["cols"]        # the number of columns
    rowsum = instance["rowsum"]    # rowsum[r]: the number of ship squares in row r
    colsum = instance["colsum"]    # colsum[c]: the number of ship squares in column c
    fleet = {size: count for size, count in instance["fleet_counts"]}  # fleet[n]: how many ships of n squares
    hints = instance["hints"]      # the squares whose content is shown in the puzzle
    WATER, CIRCLE = instance["WATER"], instance["CIRCLE"]  # the values of water and of a one-square ship
    LEFT, RIGHT = instance["LEFT"], instance["RIGHT"]      # the values of the left and right ends of a ship
    TOP, BOTTOM = instance["TOP"], instance["BOTTOM"]      # the values of the top and bottom ends of a ship
    MIDDLE = instance["MIDDLE"]                            # the value of a square inside a longer ship

    # There is no objective: any grid that meets the rules is a solution.
    problem = pulp.LpProblem("solitaire_battleships", pulp.LpMinimize)

    # Each cell is in exactly one of these states: W water; C a one-square ship;
    # L and R the left and right ends of a ship lying in a row; T and B the top and bottom
    # ends of a ship lying in a column; H a middle square of a ship lying in a row; V a
    # middle square of a ship lying in a column.
    states = ["W", "C", "L", "R", "T", "B", "H", "V"]
    # the value that the grid shows for each state
    code = {"W": WATER, "C": CIRCLE, "L": LEFT, "R": RIGHT, "T": TOP, "B": BOTTOM,
            "H": MIDDLE, "V": MIDDLE}
    # state[(r, c)][s] is 1 when cell (r, c) is in state s, and 0 when not
    state = {(r, c): {s: pulp.LpVariable(f"state_{r}_{c}_{s}", cat="Binary") for s in states}
             for r in range(rows) for c in range(cols)}

    # 1 if cell (r, c) holds any part of a ship
    def ship(r, c):
        return 1 - state[(r, c)]["W"]

    # whether cell (r, c) lies on the grid
    def inside(r, c):
        return 0 <= r < rows and 0 <= c < cols

    # Every cell is in exactly one state.
    for cell in state:
        problem += pulp.lpSum(state[cell].values()) == 1

    # A square whose content is shown holds that content. The shown middle value fits
    # either a horizontal or a vertical middle square.
    for r, c, value in hints:
        problem += pulp.lpSum(state[(r, c)][s] for s in states if code[s] == value) == 1

    # Each row and column has the given number of ship squares.
    for r in range(rows):
        problem += pulp.lpSum(ship(r, c) for c in range(cols)) == rowsum[r]
    for c in range(cols):
        problem += pulp.lpSum(ship(r, c) for r in range(rows)) == colsum[c]

    # Ships do not touch diagonally: of two diagonal neighbours at most one is a ship
    # square. Touching along a row or column is ruled out by the part rules below.
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((1, 1), (1, -1)):
                if inside(r + dr, c + dc):
                    problem += ship(r, c) + ship(r + dr, c + dc) <= 1

    # If the cell is in cell_state, each listed neighbour on the grid is water.
    def need_water(cell_state, r, c, neighbours):
        nonlocal problem
        for dr, dc in neighbours:
            if inside(r + dr, c + dc):
                problem += cell_state + ship(r + dr, c + dc) <= 1

    # If the cell is in cell_state, its neighbour at (dr, dc) is in one of `wanted`.
    # Off the grid there is no neighbour, so the cell cannot be in cell_state.
    def need_one_of(cell_state, r, c, dr, dc, wanted):
        nonlocal problem
        if inside(r + dr, c + dc):
            problem += cell_state <= pulp.lpSum(state[(r + dr, c + dc)][s] for s in wanted)
        else:
            problem += cell_state == 0

    for r in range(rows):
        for c in range(cols):
            cell = state[(r, c)]
            up, down, west, east = (-1, 0), (1, 0), (0, -1), (0, 1)
            # A one-square ship is surrounded by water.
            need_water(cell["C"], r, c, [up, down, west, east])
            # The left end of a ship continues to the east, and the other three sides are water.
            need_one_of(cell["L"], r, c, 0, 1, ["H", "R"])
            need_water(cell["L"], r, c, [up, down, west])
            # The right end of a ship continues to the west, and the other three sides are water.
            need_one_of(cell["R"], r, c, 0, -1, ["H", "L"])
            need_water(cell["R"], r, c, [up, down, east])
            # The top end of a ship continues to the south, and the other three sides are water.
            need_one_of(cell["T"], r, c, 1, 0, ["V", "B"])
            need_water(cell["T"], r, c, [up, west, east])
            # The bottom end of a ship continues to the north, and the other three sides are water.
            need_one_of(cell["B"], r, c, -1, 0, ["V", "T"])
            need_water(cell["B"], r, c, [down, west, east])
            # A middle square of a row ship has ship squares on its west and east, and water north and south.
            need_one_of(cell["H"], r, c, 0, -1, ["L", "H"])
            need_one_of(cell["H"], r, c, 0, 1, ["R", "H"])
            need_water(cell["H"], r, c, [up, down])
            # A middle square of a column ship has ship squares on its north and south, and water west and east.
            need_one_of(cell["V"], r, c, -1, 0, ["T", "V"])
            need_one_of(cell["V"], r, c, 1, 0, ["B", "V"])
            need_water(cell["V"], r, c, [west, east])

    # The fleet has the given number of one-square ships.
    problem += pulp.lpSum(state[cell]["C"] for cell in state) == fleet.get(1, 0)

    # A ship of n >= 2 squares is an end square, n-2 middle squares and the opposite end
    # square, in a line. line[(n, 'h' or 'v', r, c)] is 1 when such a ship starts at (r, c)
    # and lies in that direction. The flag is 1 exactly when all its squares are in place,
    # so it counts the ships present.
    for size, count in fleet.items():
        if size < 2:
            continue
        lines = []
        for r in range(rows):
            for c in range(cols):
                for orientation in ("h", "v"):
                    dr, dc = (0, 1) if orientation == "h" else (1, 0)
                    if not inside(r + dr * (size - 1), c + dc * (size - 1)):
                        continue
                    first, last, mid = ("L", "R", "H") if orientation == "h" else ("T", "B", "V")
                    parts = [state[(r, c)][first], state[(r + dr * (size - 1), c + dc * (size - 1))][last]]
                    parts += [state[(r + dr * k, c + dc * k)][mid] for k in range(1, size - 1)]
                    line = pulp.LpVariable(f"line_{size}_{orientation}_{r}_{c}", cat="Binary")
                    for part in parts:
                        problem += line <= part
                    problem += line >= pulp.lpSum(parts) - (size - 1)
                    lines.append(line)
        problem += pulp.lpSum(lines) == count

    # Every left or top end starts a ship of the fleet, so no ship has a size the fleet
    # does not list.
    problem += pulp.lpSum(state[cell]["L"] + state[cell]["T"] for cell in state) == sum(
        count for size, count in fleet.items() if size > 1)

    # grid[r][c] is the value shown in cell (r, c)
    grid = [[pulp.lpSum(code[s] * state[(r, c)][s] for s in states) for c in range(cols)]
            for r in range(rows)]
    return problem, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
