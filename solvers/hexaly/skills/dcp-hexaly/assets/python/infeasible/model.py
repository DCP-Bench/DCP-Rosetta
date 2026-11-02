"""Three talks in two rooms, every pair of talks overlaps: no assignment exists.

As hard constraints Hexaly may only report INFEASIBLE (nothing found, no proof). Counting the
clashes and minimising them proves the minimum is 1, so no clash-free assignment exists.
The hard model is here only to show its status: the soft model alone also finds a clash-free
assignment when one exists (minimum 0).
"""
import hexaly.optimizer as hx

S = hx.HxSolutionStatus
TALKS, ROOMS = 3, 2


def solve(soft):
    with hx.HexalyOptimizer() as optimizer:
        optimizer.param.verbosity = 0
        optimizer.param.nb_threads = 4
        optimizer.param.set_gap_limit(0)
        optimizer.param.time_limit = 3
        model = optimizer.model
        room = [model.int(0, ROOMS - 1) for _ in range(TALKS)]
        clash = [room[a] == room[b] for a in range(TALKS) for b in range(a + 1, TALKS)]
        if soft:
            # Each pair of talks in the same room counts as one clash
            model.minimize(model.sum(clash))
        else:
            # No two talks share a room
            for c in clash:
                model.constraint(model.not_(c))
            model.minimize(0)
        model.close()
        optimizer.solve()
        solution = optimizer.solution
        if soft and solution.status == S.OPTIMAL:
            return solution.status.name, model.get_objective(0).value
        return solution.status.name, None


print("Hard model:", solve(soft=False)[0])
status, clashes = solve(soft=True)
print("Soft model:", status, "minimum clashes:", clashes)
if status == "OPTIMAL" and clashes >= 1:
    print("Proven infeasible")
