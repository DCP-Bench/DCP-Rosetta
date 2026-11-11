# csplib_006_golomb_rulers: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from docplex.mp.model import Model


def create_model(instance):
    """Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_m so that the
    m(m-1)/2 differences a_j - a_i (i < j) are all different, with the ruler as short as possible."""
    size = instance["size"]  # number of marks
    # The problem gives the marks no upper limit; they are kept within 0..horizon so that every
    # variable is finite. A shortest ruler is no longer than any Golomb ruler with `size` marks,
    # such as the greedy one built here (each next mark at the smallest position that keeps all
    # differences distinct), and size * size also bounds it, so horizon is the shorter of the
    # two lengths. This removes only rulers that cannot be optimal.
    greedy = [0]
    differences = set()
    while len(greedy) < size:
        p = greedy[-1] + 1
        while any(p - q in differences for q in greedy):
            p += 1
        differences |= {p - q for q in greedy}
        greedy.append(p)
    horizon = min(size * size, greedy[-1])

    model = Model("golomb_ruler")

    # marks[i] is the position of mark i on the ruler.
    marks = [model.integer_var(0, horizon, name=f"mark_{i}") for i in range(size)]

    # The first mark is at 0.
    model.add_constraint(marks[0] == 0)

    # The marks are strictly increasing along the ruler.
    model.add_constraints(marks[i] + 1 <= marks[i + 1] for i in range(size - 1))

    def distance(i, j):
        return marks[j] - marks[i]

    # All differences a_j - a_i are different. With increasing marks, two differences whose
    # intervals are nested (one interval inside the other, sharing an end or not) are already
    # different. Two crossing intervals i < k < j < l have equal differences exactly when the
    # disjoint intervals [i, k] and [j, l] do (a_j - a_i = a_l - a_k is a_k - a_i = a_l - a_j).
    # So it is enough to separate every pair of intervals that do not overlap, [i, j] and
    # [k, l] with j <= k: C(size, 4) + C(size, 3) pairs instead of all C(C(size, 2), 2), which
    # keeps size 10 inside the Community Edition's 1000 constraints.
    for i in range(size):
        for j in range(i + 1, size):
            for k in range(j, size):
                for l in range(k + 1, size):
                    # longer is 1 when [k, l] is the longer of the two, 0 when [i, j] is.
                    longer = model.binary_var(name=f"longer_{i}_{j}_{k}_{l}")
                    model.add_indicator(longer, distance(i, j) + 1 <= distance(k, l), active_value=1)
                    model.add_indicator(longer, distance(k, l) + 1 <= distance(i, j), active_value=0)

    # Implied constraints, added to strengthen the relaxation (they cut off no ruler): the marks a..b form a
    # ruler of their own with C(b - a + 1, 2) different positive differences. The largest of
    # them, a_b - a_a, is at least that count, and together they add up to at least
    # 1 + 2 + ... + that count.
    for a in range(size):
        for b in range(a + 1, size):
            count = (b - a + 1) * (b - a) // 2
            model.add_constraint(distance(a, b) >= count)
            model.add_constraint(
                model.sum(distance(i, j) for i in range(a, b + 1) for j in range(i + 1, b + 1))
                >= count * (count + 1) // 2)

    # The length of the ruler is the position of its last mark.
    length = marks[size - 1]

    # Objective: the shortest ruler.
    model.minimize(length)

    return model, {"marks": marks, "length": length}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
