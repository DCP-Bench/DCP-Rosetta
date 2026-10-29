Blind model, after reading the lessons of 20261016-maxicp-java-models (8x8 finds 36 fast but
never proves it). The rules are one (cell, live-neighbour count) table per grid cell and per dead
cell of the ring just outside. What closes the proof is an implied bound: any 3x3 square holds at
most 6 live cells. It was checked exhaustively before use (a host script over every 3x3 pattern
with 7+ live cells and every assignment of the 16 cells around it: none lets all nine cells obey
the rules). Each 3x3 window is bounded, and the objective is also posted as the sum over 3x3
blocks tiling the grid in all nine offsets, so the bounds limit the objective during search.
Live cells are tried first (cell = not(registered Boolean)). 8x8: optimum proven in about 20 s,
one optimal pattern reported and the enumeration completes (the evaluator accepted it).
