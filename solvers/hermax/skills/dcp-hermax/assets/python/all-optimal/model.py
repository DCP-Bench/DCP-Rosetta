# Every minimum vertex cover of a small graph.
from hermax.model import Model

N = 6                                                     # the number of vertices
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5)]  # the edges to cover

m = Model()
# take[v] is true when vertex v is in the cover
take = m.bool_vector("take", N)

# Every edge has at least one of its ends in the cover.
for u, v in EDGES:
    m &= (take[u] | take[v])

# Take as few vertices as possible.
m.obj += sum(take[v] for v in range(N))

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
best = r.cost
print(f"minimum cover size {best}")

# Forbid each optimal cover in turn. The next solve finds the next-best cover;
# stop as soon as it costs more than the optimum.
count = 0
while r.status == "optimum" and r.cost == best:
    chosen = [bool(r[t]) for t in take]
    print([v for v in range(N) if chosen[v]])
    count += 1
    block = None
    for var, value in zip(take, chosen):
        literal = ~var if value else var
        block = literal if block is None else (block | literal)
    m &= block
    r = m.solve()
print(f"{count} optimal covers")
