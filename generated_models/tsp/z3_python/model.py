# tsp: a Z3 (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python tsp.py tsp.json

import math

import z3


def nearest_route_length(dist):
    """Length of a short route: from every start city, always go to the nearest
    city not yet visited, then shorten the route by reversing stretches of it
    while that helps. Every route is at least the shortest one, so this is an
    upper bound on the shortest route."""
    n_cities = len(dist)

    def route_length(route):
        return sum(dist[route[k]][route[(k + 1) % n_cities]] for k in range(n_cities))

    best_route = None
    for start in range(n_cities):
        route, visited = [start], {start}
        while len(route) < n_cities:
            here = route[-1]
            nxt = min((j for j in range(n_cities) if j not in visited), key=lambda j: dist[here][j])
            route.append(nxt)
            visited.add(nxt)
        improved = True
        while improved:
            improved = False
            for a in range(n_cities - 1):
                for b in range(a + 2, n_cities):
                    p, q = route[a], route[a + 1]
                    r, s = route[b], route[(b + 1) % n_cities]
                    if p == s:
                        continue
                    if dist[p][r] + dist[q][s] < dist[p][q] + dist[r][s]:
                        route[a + 1:b + 1] = reversed(route[a + 1:b + 1])
                        improved = True
        if best_route is None or route_length(route) < route_length(best_route):
            best_route = route
    return route_length(best_route)


def assignment_bound(dist):
    """Cheapest way to give every city one departing route arc and one arriving
    route arc, ignoring whether the arcs form a single route. Every route is such
    an assignment, so its cost is a lower bound on the shortest route.

    Returns the bound and the potentials row and col (1-based) with
    dist[i][j] - row[i] - col[j] >= 0 for every arc. The sum of the potentials is
    the bound, and every route's length is that sum plus the reduced distances
    of its arcs."""
    n_cities = len(dist)
    big = sum(max(r) for r in dist) + 1  # cost of a city leaving to itself, which no route does
    row = [0] * (n_cities + 1)           # row[i]: potential of departing city i
    col = [0] * (n_cities + 1)           # col[j]: potential of arriving city j
    owner = [0] * (n_cities + 1)         # owner[j]: the departing city assigned to arriving city j
    for i in range(1, n_cities + 1):
        owner[0] = i
        j0 = 0
        least = [math.inf] * (n_cities + 1)  # least[j]: cheapest reduced cost found so far to arriving city j
        via = [0] * (n_cities + 1)           # via[j]: the arriving city that cheapest cost comes from
        used = [False] * (n_cities + 1)      # used[j]: arriving city j is already in the search tree
        while True:
            used[j0] = True
            i0, delta, j1 = owner[j0], math.inf, 0
            for j in range(1, n_cities + 1):
                if not used[j]:
                    c = (big if i0 == j else dist[i0 - 1][j - 1]) - row[i0] - col[j]
                    if c < least[j]:
                        least[j], via[j] = c, j0
                    if least[j] < delta:
                        delta, j1 = least[j], j
            for j in range(n_cities + 1):
                if used[j]:
                    row[owner[j]] += delta
                    col[j] -= delta
                else:
                    least[j] -= delta
            j0 = j1
            if owner[j0] == 0:
                break
        while j0:
            j1 = via[j0]
            owner[j0] = owner[j1]
            j0 = j1
    return sum(row[1:]) + sum(col[1:]), row, col


def held_karp_exclusions(dist, upper):
    """Edges that no route shorter than or equal to upper can use, found with
    1-trees: a spanning tree on cities 1 .. n-1 plus two edges at city 0. Returns
    a set of pairs (i, j), i < j, for edges that are ruled out in both directions."""
    n_cities = len(dist)
    excluded = set()
    if n_cities <= 2:
        return excluded

    def one_tree(pi):
        """Cheapest 1-tree when each edge (i, j) costs dist[i][j] + pi[i] + pi[j],
        minus 2 * sum(pi). Every route is a 1-tree, so this is a lower bound on the
        shortest route for any pi."""
        def cost(i, j):
            return dist[i][j] + pi[i] + pi[j]
        parent, degree, total = {}, [0] * n_cities, 0.0
        # Prim's algorithm over cities 1 .. n-1
        frontier = {v: (cost(1, v), 1) for v in range(2, n_cities)}
        while frontier:
            v = min(frontier, key=lambda x: frontier[x][0])
            c, par = frontier.pop(v)
            total += c
            parent[v] = par
            degree[v] += 1
            degree[par] += 1
            for x in frontier:
                cx = cost(v, x)
                if cx < frontier[x][0]:
                    frontier[x] = (cx, v)
        # the two cheapest edges at city 0
        ends = sorted(range(1, n_cities), key=lambda j: cost(0, j))[:2]
        for j in ends:
            total += cost(0, j)
            degree[0] += 1
            degree[j] += 1
        return total - 2 * sum(pi), parent, ends, degree, cost

    # Subgradient steps on pi raise the bound.
    pi, best_pi, best_bound = [0.0] * n_cities, [0.0] * n_cities, -math.inf
    step, stall = 2.0, 0
    for _ in range(1000):
        bound, _, _, degree, _ = one_tree(pi)
        if bound > best_bound + 1e-9:
            best_bound, best_pi, stall = bound, list(pi), 0
        else:
            stall += 1
            if stall >= 10:
                step, stall = step / 2, 0
        # gradient[i]: how far city i is from having exactly two route edges
        gradient = [degree[i] - 2 for i in range(n_cities)]
        norm = sum(g * g for g in gradient)
        if norm == 0 or step < 1e-4 or upper - bound <= 1e-9:
            break  # the 1-tree is a route, or the bound has stopped rising
        t = step * (upper - bound) / norm
        pi = [pi[i] + t * gradient[i] for i in range(n_cities)]

    # An edge (i, j) forced into a 1-tree costs at least the cheapest 1-tree plus the
    # edge's cost minus the dearest tree edge it replaces. If that exceeds upper, no
    # route of length at most upper uses the edge. The margin only keeps edges.
    bound, parent, ends, _, cost = one_tree(best_pi)
    tree = {v: [] for v in range(1, n_cities)}  # tree[v]: the tree neighbours of city v
    for v, par in parent.items():
        tree[v].append(par)
        tree[par].append(v)
    for i in range(1, n_cities):
        # longest[v]: the dearest tree edge on the tree path from city i to city v
        longest, stack = {i: -math.inf}, [i]
        while stack:
            v = stack.pop()
            for x in tree[v]:
                if x not in longest:
                    longest[x] = max(longest[v], cost(v, x))
                    stack.append(x)
        for j in range(i + 1, n_cities):
            if parent.get(j) == i or parent.get(i) == j:
                continue
            if bound + cost(i, j) - longest[j] > upper + 1e-6:
                excluded.add((i, j))
    dearer = max(cost(0, j) for j in ends)  # the dearer of the two chosen edges at city 0
    for j in range(1, n_cities):
        if j not in ends and bound + cost(0, j) - dearer > upper + 1e-6:
            excluded.add((0, j))
    return excluded


def create_model(instance):
    """Travelling salesman: find the shortest route that visits every city exactly
    once and returns to the starting city. The distance between two cities is the
    Euclidean distance between their locations, rounded to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) position of city i
    n_cities = len(locations)          # the number of cities

    # dist[i][j]: the distance between city i and city j
    dist = [[int(round(math.dist(a, b))) for b in locations] for a in locations]

    if n_cities == 1:
        # a single city: the route stays where it is, so its length is 0
        solver = z3.Optimize()
        travel_distance = z3.IntVal(0)
        solver.minimize(travel_distance)
        return solver, {"travel_distance": travel_distance}

    # upper bounds the shortest route from above, lower from below
    upper = nearest_route_length(dist)
    lower, row, col = assignment_bound(dist)
    # reduced[i][j]: the distance from city i to city j less the two potentials
    reduced = [[dist[i][j] - row[i + 1] - col[j + 1] for j in range(n_cities)] for i in range(n_cities)]
    excluded = held_karp_exclusions(dist, upper)

    # succ[i][j] is true when the route goes directly from city i to city j
    succ = [[z3.Bool(f"succ_{i}_{j}") if i != j else None for j in range(n_cities)] for i in range(n_cities)]
    arcs = [(i, j) for i in range(n_cities) for j in range(n_cities) if i != j]

    # ge[i][t] (t = 2 .. n-1) is true when city i is at position t or later on the
    # route. Positions 1 .. n-1 are the visiting order after the start city 0.
    ge = {i: {t: z3.Bool(f"pos_{i}_ge_{t}") for t in range(2, n_cities)} for i in range(1, n_cities)}

    def at_least(i, t):
        if t <= 1:
            return z3.BoolVal(True)
        if t >= n_cities:
            return z3.BoolVal(False)
        return ge[i][t]

    solver = z3.Optimize()

    # Every city is left exactly once and entered exactly once.
    for i in range(n_cities):
        solver.add(z3.PbEq([(succ[i][j], 1) for j in range(n_cities) if j != i], 1))
        solver.add(z3.PbEq([(succ[j][i], 1) for j in range(n_cities) if j != i], 1))

    if n_cities > 2:
        # The route never steps straight back to the city it came from.
        for i in range(n_cities):
            for j in range(i + 1, n_cities):
                solver.add(z3.Or(z3.Not(succ[i][j]), z3.Not(succ[j][i])))

        # A city at position t+1 or later is also at position t or later.
        for i in range(1, n_cities):
            for t in range(2, n_cities - 1):
                solver.add(z3.Implies(ge[i][t + 1], ge[i][t]))

        # Leaving city 0 for city i makes i the first city after 0, and returning
        # from city i to city 0 makes i the last one.
        for i in range(1, n_cities):
            solver.add(z3.Implies(succ[0][i], z3.Not(at_least(i, 2))))
            solver.add(z3.Implies(succ[i][0], at_least(i, n_cities - 1)))

        # Going from city i to city j (neither is city 0) puts j one position after i.
        # A cycle that avoids city 0 would need positions that grow all the way
        # round, which is impossible.
        for i in range(1, n_cities):
            for j in range(1, n_cities):
                if i != j:
                    for t in range(1, n_cities):
                        solver.add(z3.Implies(succ[i][j], at_least(i, t) == at_least(j, t + 1)))

        # Each position 1 .. n-1 is taken by exactly one city.
        for t in range(1, n_cities):
            solver.add(z3.PbEq([(z3.And(at_least(i, t), z3.Not(at_least(i, t + 1))), 1)
                                for i in range(1, n_cities)], 1))

        # A route and the same route travelled backwards have the same length.
        # Requiring city 2 to come after city 1 keeps one direction of each route.
        for t in range(1, n_cities):
            solver.add(z3.Implies(at_least(1, t), at_least(2, t + 1)))

    # A route that uses an arc is at least lower plus that arc's reduced distance,
    # since reduced distances are not negative. An arc is ruled out when that
    # exceeds upper, or when the 1-tree test excluded its edge.
    slack = upper - lower  # the gap between the upper and lower bounds
    for i, j in arcs:
        if reduced[i][j] > slack or (min(i, j), max(i, j)) in excluded:
            solver.add(z3.Not(succ[i][j]))

    # The reduced distances of the arcs used add up to at most the gap, so the
    # route is no longer than upper.
    weighted = [(succ[i][j], reduced[i][j]) for i, j in arcs if reduced[i][j] > 0]
    if weighted:
        solver.add(z3.PbLe(weighted, slack))

    # travel_distance: the length of the route, which is the lower bound plus the
    # reduced distances of the arcs used.
    travel_distance = z3.Sum([z3.IntVal(lower)] + [z3.If(lit, w, 0) for lit, w in weighted])

    solver.minimize(travel_distance)

    return solver, {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
