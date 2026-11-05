"""Complete a 4x4 Latin square: every row and every column holds 1..4 once, four cells are given."""
import hexaly.optimizer as hx

N = 4
GIVEN = {(0, 0): 1, (1, 1): 3, (2, 3): 2, (3, 2): 4}

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0  # the log goes to stdout otherwise
    optimizer.param.time_limit = 10  # whole seconds
    model = optimizer.model
    cell = [[model.int(1, N) for _ in range(N)] for _ in range(N)]

    # Each row holds N different values
    for r in range(N):
        model.constraint(model.count(model.distinct(model.array(cell[r]))) == N)
    # Each column holds N different values
    for c in range(N):
        model.constraint(model.count(model.distinct(model.array([cell[r][c] for r in range(N)]))) == N)
    # The given cells keep their values
    for (r, c), v in GIVEN.items():
        model.constraint(cell[r][c] == v)

    # Hexaly needs an objective; a constant one turns this into a feasibility problem
    model.minimize(0)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("Status:", status.name)
    if status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        grid = [[cell[r][c].value for c in range(N)] for r in range(N)]
        for row in grid:
            print(" ".join(map(str, row)))
        rows_ok = all(sorted(row) == list(range(1, N + 1)) for row in grid)
        cols_ok = all(sorted(grid[r][c] for r in range(N)) == list(range(1, N + 1)) for c in range(N))
        print("Latin square:", rows_ok and cols_ok)
