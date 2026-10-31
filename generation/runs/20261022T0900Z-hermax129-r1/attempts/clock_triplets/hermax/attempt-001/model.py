"""
Model for clock_triplets problem.

Rearrange numbers 1-12 on a clock face such that no triplet of adjacent numbers
sums to more than 21. The arrangement is circular (position 12 wraps to position 1).
"""
from hermax.model import Model


def build(instance):
    m = Model()

    # Create arrangement of 12 numbers on the clock
    # x[i] contains the number at position i (0-indexed)
    x = m.int_vector("x", 12, 1, 12)

    # All numbers 1-12 must appear exactly once
    m &= x.all_different()

    # Constraint: no three adjacent numbers sum to more than 21
    # The arrangement is circular, so position 12 wraps to position 1
    for i in range(12):
        # Three consecutive positions: i, (i+1)%12, (i+2)%12
        triplet_sum = x[i] + x[(i+1) % 12] + x[(i+2) % 12]
        m &= (triplet_sum <= 21)

    return m, {"x": x}
