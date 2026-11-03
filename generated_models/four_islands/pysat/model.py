# four_islands: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python four_islands.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Four islands on a square map, joined by bridges, each with its own name, export and tourist
    attraction. Find the name, export and attraction of each island from six clues about where
    the islands lie."""
    n = 4
    a, b, c, d = range(n)  # map positions: a north-west, b north-east, c south-west, d south-east

    # The map row of position p: 0 for the north, 1 for the south.
    def row(p):
        return p // 2

    # The map column of position p: 0 for the west, 1 for the east.
    def column(p):
        return p % 2

    # Position q is due south of position p.
    def due_south(p, q):
        return column(p) == column(q) and row(q) == row(p) + 1

    # Position p is due west of position q.
    def due_west(p, q):
        return row(p) == row(q) and column(p) + 1 == column(q)

    # Positions p and q are joined by a north-south bridge.
    def north_south_bridge(p, q):
        return column(p) == column(q) and row(p) != row(q)

    # Positions p and q are joined by an east-west bridge.
    def east_west_bridge(p, q):
        return row(p) == row(q) and column(p) != column(q)

    # Positions p and q are joined by a bridge.
    def connected(p, q):
        return north_south_bridge(p, q) or east_west_bridge(p, q)

    pool = IDPool()

    # Four map positions, one for each of four islands, exports or attractions.
    def positions(name):
        return [Integer(f"{name}{i}", 0, n - 1, vpool=pool) for i in range(n)]

    # island[i] is the map position of the i-th island: Pwana, Quero, Rayou, Skern.
    island = positions("island")
    pwana, quero, rayou, skern = island
    # export[i] is the map position of the island exporting alabaster, bananas, coconuts or durian fruit.
    export = positions("export")
    alabaster, bananas, coconuts, durian_fruit = export
    # attraction[i] is the map position of the island with the resort hotel, the ice skating rink,
    # the jai alai stadium or the koala preserve.
    attraction = positions("attraction")
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # Every island, export and attraction, as the variables of the constraints.
    variables = island + export + attraction
    engine = IntegerEngine(vars=variables, vpool=pool)

    # Each island has a different name, each export a different island, each attraction a different island.
    engine.add_alldifferent(island)
    engine.add_alldifferent(export)
    engine.add_alldifferent(attraction)

    cnf = engine.clausify()

    # The positions of x and y must make the clue hold. Every other pair of positions is ruled out.
    def require(x, y, holds):
        for p in range(n):
            for q in range(n):
                if not holds(p, q):
                    cnf.append([-x.equals(p), -y.equals(q)])

    # The island with the koala preserve is due south of Pwana.
    require(pwana, koala_preserve, due_south)
    # The island with the largest alabaster quarry is due west of Quero.
    require(alabaster, quero, due_west)
    # The island with the resort hotel is due east of the island exporting durian fruit.
    require(durian_fruit, resort_hotel, due_west)
    # Skern and the jai alai stadium are joined by a north-south bridge.
    require(skern, jai_alai_stadium, north_south_bridge)
    # Rayou and the island exporting bananas are joined by an east-west bridge.
    require(rayou, bananas, east_west_bridge)
    # The ice skating rink and the jai alai stadium are different islands, not joined by a bridge.
    require(ice_skating_rink, jai_alai_stadium, lambda p, q: p != q and not connected(p, q))

    return cnf, {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
