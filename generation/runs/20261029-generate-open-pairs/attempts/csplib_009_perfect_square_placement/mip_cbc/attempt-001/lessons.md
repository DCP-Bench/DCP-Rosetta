Blind model: exact cover. One binary per square and corner position, every cell of the base square
covered exactly once (the areas add up to base^2). Evaluated: 4 of 6 accepted (example, json:1,
json:3, json:4); json:5 (19 squares in 30x30, 12463 binaries, 455k nonzeros) and json:6 (21 squares
in 112x112) end in memory_limit. CBC's log on json:5 (local, 2048 MB): clique strengthening 85 s,
conflict graph 125 s, then no solution. Locally also tried, both timing out on json:5 with no
solution: presolve off or cuts off; and one-hot x and y positions with pairwise big-M non-overlap
plus the exact strip sums (11.5k nodes in 170 s, no solution).
