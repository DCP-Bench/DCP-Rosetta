# Four tasks on one shared resource of capacity 2, with precedences. Minimise the makespan.
from hermax.model import Model

NAMES = ["A", "B", "C", "D"]  # the tasks
DURATION = [3, 2, 4, 2]       # DURATION[i]: how long task i runs
DEMAND = [1, 1, 2, 1]         # DEMAND[i]: resource units task i uses while it runs
CAPACITY = 2                  # resource units available at any time
PRECEDES = [(0, 2), (1, 3)]   # (a, b): task a must finish before task b starts
HORIZON = sum(DURATION)       # no schedule needs longer than all tasks in a row

m = Model()
# start[i] is when task i starts; makespan is when the last task ends
start = m.int_vector("start", len(NAMES), 0, HORIZON)
makespan = m.int("makespan", 0, HORIZON)

# Every task ends by the makespan.
for i, d in enumerate(DURATION):
    m &= (start[i] + d <= makespan)
# Each precedence: the first task finishes before the second starts.
for a, b in PRECEDES:
    m &= (start[a] + DURATION[a] <= start[b])
# The running tasks never use more than the capacity.
m &= m.cumulative(start, DURATION, DEMAND, CAPACITY)
# Finish as early as possible.
m.obj += makespan

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
for i, name in enumerate(NAMES):
    print(f"{name}: starts {r[start[i]]}, runs {DURATION[i]}")
print(f"Makespan: {r.cost}")
