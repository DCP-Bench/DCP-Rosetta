# Assign four workers to four jobs, one job each, at the lowest total cost.
from hermax.model import Model

COST = [         # COST[i][j]: what worker i charges for job j
    [9, 2, 7, 8],
    [6, 4, 3, 7],
    [5, 8, 1, 8],
    [7, 6, 9, 4],
]
N = len(COST)

m = Model()
# x[i][j] is true when worker i does job j
x = m.bool_matrix("x", N, N)

# Every worker does exactly one job, and every job is done by exactly one worker.
for i in range(N):
    m &= x.row(i).exactly_one()
for j in range(N):
    m &= x.col(j).exactly_one()

# Pay as little as possible in total.
m.obj += sum(COST[i][j] * x[i][j] for i in range(N) for j in range(N))

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
assigned = [next(j for j in range(N) if r[x[i][j]]) for i in range(N)]
print("job of each worker:", assigned)
print(f"Total cost: {r.cost}")
