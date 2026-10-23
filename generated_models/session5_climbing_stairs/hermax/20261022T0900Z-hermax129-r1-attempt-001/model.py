from hermax.model import Model


def build(instance):
    n = instance["n"]
    m1 = instance["m1"]
    m2 = instance["m2"]

    # steps[i] is the number of stairs climbed at move i. Each move climbs
    # m1 to m2 steps, or 0 once the top has been reached. At most n moves
    # are needed, since every real move climbs at least one step.
    m = Model()
    steps = m.int_vector("steps", n, 0, m2)

    # Each move is either 0 (no move) or between m1 and m2 steps.
    for i in range(n):
        m &= ((steps[i] == 0) | (steps[i] >= m1))

    # Together the moves reach the top of the stair exactly.
    m &= (sum(steps[i] for i in range(n)) == n)

    # Once a move is 0 (the top is reached), all later moves are 0 too.
    for i in range(n - 1):
        m &= (steps[i + 1] == 0).only_if(steps[i] == 0)

    return m, {"steps": steps}
