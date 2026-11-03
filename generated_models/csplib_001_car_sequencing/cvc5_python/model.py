# csplib_001_car_sequencing: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from itertools import combinations

import cvc5.pythonic as c5


def _or(items):
    # A single item stands for itself.
    if len(items) == 1:
        return items[0]
    return c5.Or(items)


def _prefix_counts(solver, flags, top, name):
    """pref[p][j], for 1 <= j <= min(p, top), is true exactly when at least j of the
    first p flags are true. Missing entries are false. The clauses that define them
    are added to solver."""
    pref = [{}]
    for p in range(1, len(flags) + 1):
        prev = pref[-1]
        cur = {}
        flag = flags[p - 1]
        for j in range(1, min(p, top) + 1):
            v = c5.Bool(f"{name}_{p}_{j}")
            cur[j] = v
            # v is true when prev[j], or when flag and prev[j - 1].
            a = prev.get(j)
            b = prev.get(j - 1) if j > 1 else None
            solver.add(_or([c5.Not(v), a, flag]) if a is not None else _or([c5.Not(v), flag]))
            if a is not None:
                solver.add(c5.Or(c5.Not(a), v))
            if j == 1:
                solver.add(c5.Or(c5.Not(flag), v))
            else:
                if a is not None and b is not None:
                    solver.add(_or([c5.Not(v), a, b]))
                elif a is None and b is not None:
                    solver.add(_or([c5.Not(v), b]))
                elif a is None and b is None:
                    solver.add(c5.Not(v))
                if b is not None:
                    solver.add(_or([c5.Not(flag), c5.Not(b), v]))
        pref.append(cur)
    return pref


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    demand = instance["demand"]        # demand[t]: number of cars of type t to build
    requires = instance["requires"]    # requires[t][o] is 1 when a car of type t needs option o
    at_most = instance["at_most"]      # at_most[o]: most cars needing option o in any window of per_slots[o] cars
    per_slots = instance["per_slots"]  # per_slots[o]: length of the window for option o

    n_types = len(demand)
    n_opts = len(at_most)
    # One position on the line for each car.
    n_cars = sum(demand)

    # type_at[p][t] is true when the car at position p has type t.
    type_at = [[c5.Bool(f"type_{p}_{t}") for t in range(n_types)] for p in range(n_cars)]
    # needs[p][o] is true when the car at position p needs option o.
    needs = [[c5.Bool(f"needs_{p}_{o}") for o in range(n_opts)] for p in range(n_cars)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each position holds exactly one car type.
    for p in range(n_cars):
        solver.add(_or(type_at[p]))
        solver.add([c5.Or(c5.Not(type_at[p][c]), c5.Not(type_at[p][d]))
                    for c, d in combinations(range(n_types), 2)])

    # Each type appears as many times on the line as it is demanded.
    for c in range(n_types):
        d = demand[c]
        if d == 0:
            solver.add([c5.Not(type_at[p][c]) for p in range(n_cars)])
            continue
        pref = _prefix_counts(solver, [type_at[p][c] for p in range(n_cars)], d + 1, f"dem_{c}")
        solver.add(pref[n_cars][d])
        if (d + 1) in pref[n_cars]:
            solver.add(c5.Not(pref[n_cars][d + 1]))

    # A position needs option o exactly when its car type needs o.
    for p in range(n_cars):
        for o in range(n_opts):
            types_needing_o = [c for c in range(n_types) if requires[c][o] == 1]
            if types_needing_o:
                solver.add(needs[p][o] == _or([type_at[p][c] for c in types_needing_o]))
            else:
                solver.add(c5.Not(needs[p][o]))

    # Station capacity: in each window of per_slots[o] consecutive positions, no
    # at_most[o] + 1 positions all need option o. A window shorter than that has
    # nothing to forbid.
    for o in range(n_opts):
        w = per_slots[o]
        k = at_most[o]
        if k + 1 > w:
            continue
        for start in range(n_cars - w + 1):
            for subset in combinations(range(start, start + w), k + 1):
                solver.add(_or([c5.Not(needs[p][o]) for p in subset]))

    # Consequences of the windows and the demand, which narrow the search. The
    # cars needing option o in the whole sequence are total_o. Any m consecutive
    # positions hold at most cap(m) of them, with cap(m) = (m // w) * k + min(k, m % w),
    # so the first n_cars - m positions hold at least total_o - cap(m).
    for o in range(n_opts):
        w = per_slots[o]
        k = at_most[o]
        total_o = sum(demand[c] for c in range(n_types) if requires[c][o] == 1)
        pref = _prefix_counts(solver, [needs[p][o] for p in range(n_cars)], total_o + 1, f"opt_{o}")
        if total_o > 0:
            solver.add(pref[n_cars][total_o])
        if (total_o + 1) in pref[n_cars]:
            solver.add(c5.Not(pref[n_cars][total_o + 1]))
        for m in range(1, n_cars + 1):
            cap = (m // w) * k + min(k, m % w)
            if (cap + 1) in pref[m]:
                solver.add(c5.Not(pref[m][cap + 1]))
            low = total_o - cap
            if low > 0 and (n_cars - m) >= 1:
                if low in pref[n_cars - m]:
                    solver.add(pref[n_cars - m][low])
                else:
                    solver.add(c5.BoolVal(False))

    # The car type at each position.
    sequence = [c5.Sum([c5.If(type_at[p][c], c, 0) for c in range(n_types)])
                for p in range(n_cars)]
    return solver, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
