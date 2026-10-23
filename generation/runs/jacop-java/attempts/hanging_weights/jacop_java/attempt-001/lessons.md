# hanging_weights: lessons

- The diagram is ASCII and its vertical lines are often one character off the junction they meet.
  Reading each pivot as the nearest junction (every 3 columns on a bar) gave the bar equations. The
  two equations the description states (5*C=D, 3*G=2*(C+D)) confirmed that reading.
- The two bars whose pivots were ambiguous were the one under the top-left bar (its vertical lands
  between two junctions) and the one under the top-right bar. Pivot at the nearest junction gave
  exactly one solution by brute force, and the evaluator accepted that solution. The other choices
  gave zero solutions.
- The instance has no fields; every constant comes from the diagram and the problem statement.
