# hidato, jacop_java: lessons

- Modelled blind from the brief and the instance JSON. The instance uses 0 for an empty cell; clues stay fixed.
- Channel used: each number v has pos[v] (row-major cell), row[v], col[v] tied by pos = row*cols + col.
  The grid links to pos through Element over a 0-based index (x_i - 1), imposed with store.impose.
- Adjacency of v and v+1: |row diff| <= 1 and |col diff| <= 1. Distinct cells come from Alldifferent(pos).
- Accepted on all 5 instances with no skipped instances.
