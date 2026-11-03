# Four tasks must each get a distinct time slot out of three: no schedule exists.
from hermax.model import Model

TASKS = 4   # the number of tasks
SLOTS = 3   # the number of time slots

m = Model()
# slot[t] is the time slot of task t
slot = m.int_vector("slot", TASKS, 0, SLOTS - 1)
# No two tasks share a slot.
m &= slot.all_different()

r = m.solve()
print("status:", r.status)
if r.ok:
    print("slots:", [r[s] for s in slot])
else:
    print("no schedule: the solver proved there is none")
