# Lessons: bales_of_hay

- The description asks for the bale weights without an order. I did not add a sorted-bales constraint. The evaluator accepted the unordered model with 2 solutions on each instance, so it treats the solutions as sets of declared outputs, and the sorted reading in the instance notes is not required.
- Pairwise sums are posted as a multiset: each pair sum takes exactly one given value, and the count per distinct value equals its multiplicity in the list. A plain Alldistinct on the sums would be wrong when the list has repeats.
