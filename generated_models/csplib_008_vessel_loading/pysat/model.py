# csplib_008_vessel_loading: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def at_least(var, value):
    """Whether var is at least value, as a flag, or as True or False when every value of
    var settles it."""
    if value <= var.lb:
        return True
    if value > var.ub:
        return False
    return var.ge(value)


def negate(lit):
    """The opposite of a flag, or of a True or False constant."""
    return (not lit) if isinstance(lit, bool) else -lit


def add_clause(cnf, *lits):
    """Add the clause that holds when one of the flags or constants holds. A True constant
    satisfies the clause, and a False constant is left out of it."""
    kept = []
    for lit in lits:
        if lit is True:
            return
        if lit is not False:
            kept.append(lit)
    cnf.append(kept)


def create_model(instance):
    """Decide whether the containers can be laid out on the deck in one layer, each parallel
    to the sides of the deck, without overlapping, and with the minimum distance between
    containers of the classes that need one."""
    deck_width = instance["deck_width"]    # the deck spans 0 to deck_width across
    deck_length = instance["deck_length"]  # the deck spans 0 to deck_length along
    n = instance["n_containers"]           # the number of containers
    width = instance["width"]              # width[i]: the width of container i
    length = instance["length"]            # length[i]: the length of container i
    classes = instance["classes"]          # classes[i]: the class of container i, numbered from 1
    separation = instance["separation"]    # separation[a][b]: the minimum distance between classes a + 1 and b + 1

    pool = IDPool()  # numbers the flags used below

    # left[i] and right[i] are the edges of container i across the deck, bottom[i] and top[i]
    # are its edges along the deck. Each edge is at one position.
    left = [Integer(f"left{i}", 0, deck_width, encoding="coupled", vpool=pool) for i in range(n)]
    right = [Integer(f"right{i}", 0, deck_width, encoding="coupled", vpool=pool) for i in range(n)]
    top = [Integer(f"top{i}", 0, deck_length, encoding="coupled", vpool=pool) for i in range(n)]
    bottom = [Integer(f"bottom{i}", 0, deck_length, encoding="coupled", vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=left + right + top + bottom, vpool=pool)
    cnf = engine.clausify()  # collects the constraints on the edges

    # turned[i] is true when container i is turned, so that its length lies across the deck.
    turned = [pool.id(("turned", i)) for i in range(n)]

    def tie(low, high, size_if_upright, size_if_turned, i):
        """high = low + the container's extent: size_if_upright, or size_if_turned when it is turned."""
        for value in range(low.lb, low.ub + 1):
            for is_turned in (False, True):
                size = size_if_turned if is_turned else size_if_upright
                guard = [-turned[i]] if is_turned else [turned[i]]
                target = value + size
                if target <= high.ub:
                    cnf.append(guard + [-low.equals(value), high.equals(target)])
                else:
                    cnf.append(guard + [-low.equals(value)])

    # Each container keeps its shape. Its edges across the deck are its width, or its length
    # when it is turned. Its edges along the deck are its length, or its width when turned.
    for i in range(n):
        tie(left[i], right[i], width[i], length[i], i)
        tie(bottom[i], top[i], length[i], width[i], i)

    def before(key, first_edge, second_edge, gap):
        """A flag that, when true, forces first_edge + gap <= second_edge: for every value t,
        'first_edge >= t' implies 'second_edge >= t + gap'."""
        selector = pool.id(key)
        for t in range(first_edge.lb, first_edge.ub + 1):
            add_clause(cnf, -selector, negate(at_least(first_edge, t)), at_least(second_edge, t + gap))
        return selector

    # Two containers do not overlap. One lies at least the separation distance left of, right
    # of, below or above the other.
    for x, y in combinations(range(n), 2):
        sep = separation[classes[x] - 1][classes[y] - 1]
        cnf.append([before(("x_left_of_y", x, y), right[x], left[y], sep),
                    before(("x_right_of_y", x, y), right[y], left[x], sep),
                    before(("x_under_y", x, y), top[x], bottom[y], sep),
                    before(("x_above_y", x, y), top[y], bottom[x], sep)])

    return cnf, {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
