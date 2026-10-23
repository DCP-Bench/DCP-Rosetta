"""
Model for added_corners problem.

Grid layout with positions (left-to-right, top-to-bottom):
    0 1 2
    3   4
    5 6 7

Circles (corners): 0, 2, 5, 7
Squares (edge midpoints): 1, 3, 4, 6

Each square equals the sum of its adjoining circles:
- Square 1 (top) = Circle 0 + Circle 2
- Square 3 (left) = Circle 0 + Circle 5
- Square 4 (right) = Circle 2 + Circle 7
- Square 6 (bottom) = Circle 5 + Circle 7

All positions contain unique digits 1-8.
"""
from hermax.model import Model


def build(instance):
    m = Model()

    # Create position variables for digits 1-8
    positions = m.int_vector("positions", 8, 1, 8)

    # All positions must have different values
    m &= positions.all_different()

    # Define which positions are circles and squares
    circles = [0, 2, 5, 7]  # corners
    squares = [1, 3, 4, 6]  # edges

    # Adjacency constraints: each square equals sum of its adjoining circles
    # Square 1 (top-middle) = Circle 0 (top-left) + Circle 2 (top-right)
    m &= (positions[1] == positions[0] + positions[2])

    # Square 3 (middle-left) = Circle 0 (top-left) + Circle 5 (bottom-left)
    m &= (positions[3] == positions[0] + positions[5])

    # Square 4 (middle-right) = Circle 2 (top-right) + Circle 7 (bottom-right)
    m &= (positions[4] == positions[2] + positions[7])

    # Square 6 (bottom-middle) = Circle 5 (bottom-left) + Circle 7 (bottom-right)
    m &= (positions[6] == positions[5] + positions[7])

    return m, {"positions": positions}
