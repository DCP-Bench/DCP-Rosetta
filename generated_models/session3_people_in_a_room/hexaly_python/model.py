"""People in a room: 13 people, 4 of them male, enter one at a time with females to males never above 7/3."""
import hexaly.optimizer as hx

PEOPLE = 13
MALES = 4


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # sequence[t] = 1 if the t-th person to enter is female, 0 if male
    sequence = [model.bool() for _ in range(PEOPLE)]
    model.constraint(model.sum(sequence) == PEOPLE - MALES)

    # At every moment the ratio of females to males in the room is at most 7/3: 3 * females <= 7 * males
    for t in range(PEOPLE):
        females = model.sum(sequence[: t + 1])
        males = (t + 1) - females
        model.constraint(3 * females <= 7 * males)

    return optimizer, {"sequence": sequence}
