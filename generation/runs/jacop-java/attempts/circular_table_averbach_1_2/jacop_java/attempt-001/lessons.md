# Lessons: circular_table_averbach_1_2

- The statement's "right" is the direction of the seat numbering: the person on the right of
  seat s is (s + 1) mod 3, because 1 is right of 0 and 2 is right of 1. Passes go s -> s + 1.
- "X passed to the person who passed to the Frenchwoman" is two hops: X passes to P = x + 1,
  and P passes to the Frenchwoman, so french = (x + 2) mod 3.
- The clues leave three assignments. The evaluator accepted the model with solution limit 2.
- Model is posted with Table constraints for the two mod-3 relations, which reads closer to the
  statement than arithmetic on the seats.
