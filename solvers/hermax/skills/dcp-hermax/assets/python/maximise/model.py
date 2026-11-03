# Maximum-weight independent set: pick vertices with the largest total weight,
# no two adjacent.
from hermax.model import Model

WEIGHT = [5, 3, 8, 2, 7, 4]                                   # WEIGHT[i]: the weight of vertex i
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)]      # the pairs of adjacent vertices

m = Model()
# pick[i] is true when vertex i is in the set
pick = m.bool_vector("pick", len(WEIGHT))

# No two adjacent vertices are both picked.
for u, v in EDGES:
    m &= (~pick[u] | ~pick[v])

# Pick the heaviest set: the objective is minimised, so minimise minus the weight.
total_weight = sum(w * pick[i] for i, w in enumerate(WEIGHT))
m.obj += -total_weight

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
chosen = [i for i in range(len(WEIGHT)) if r[pick[i]]]
print("picked:", chosen)
print(f"best weight {r[total_weight]}")
