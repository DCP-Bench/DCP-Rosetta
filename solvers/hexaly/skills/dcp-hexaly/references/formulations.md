# Formulations that worked and that stalled

Hexaly finds solutions by local search and proves by bounds. A model written as a linear system over
Booleans or small integers gets both. A model that hides its structure in a permutation list, a modulo,
a product of free integers or a chain of steps often finds a solution, or nothing, and no proof. This
matters whenever you need a second solution, or the statement that no other exists, since both need a proof.

Everything below was run with Hexaly 15.0, 4 threads, one CPU, a limit of 180 s per solve. A time is the
wall-clock time to find a solution and then either a second one or a proof that there is none, for the
largest case named. "Timed out" means the first formulation ended at the limit with nothing found, or with
a solution and no proof.

## Prefer

| Problem shape | Formulation | Observed |
|---|---|---|
| A value in each cell with distinctness rules: sudoku, latin squares, hidato, magic hexagon, an order of people | one Boolean per (cell, value) with `sum == 1` per cell and per value; neighbour and arithmetic rules as linear sums over those Booleans | 9 x 9 sudokus and quasigroup completions of order up to 10: 1 s each; killer sudokus 9 x 9 with 26 to 43 cages: up to 74 s; hidato up to 12 x 12: 2.5 s, with a proof of a single solution, where a list decision found no path on the 12 x 12; magic hexagon: 66 s, a permutation list timed out; a queue of 10 people by their initials: 1 s, a list with `at` timed out |
| A walk whose next place depends on the value in this one (a frog jumping `k` places from card `k`) | a Boolean per (place, value) and a Boolean per (step, place); `at[t][p] + has[p][k] - 1 <= at[t+1][(p + k) % n]` | circles of 4, 8, 10 and 12 cards: up to 20 s, 16 cards timed out; a list with `at` and pairwise `!=` answered only the 10-card circle |
| Long sums of words or digits (a number can exceed 64 bits) | one-hot digits and one equation per column with a small integer carry | two 20-digit numbers and their sum: 1 s, a permutation list timed out; sixteen words adding to a seventh: 47 s |
| Divisibility of a growing prefix ("the first n digits are divisible by n") | one-hot digits and a quotient per prefix: `n * q[n] == 10 * (n - 1) * q[n - 1] + digit[n]`, linear | a 10-digit number divisible by 1 to 10 by prefix: 8 s with the proof that it is the only one; a list with `%` found it and timed out on the proof, also with the implied constraints below |
| Counts that must all differ (a handshake party) | a Boolean per (person, count), at most one person per count, and the count equal to the sum over the edges | parties of 1, 3, 4 and 6 couples: up to 59 s, 8 couples timed out; Booleans for the edges with pairwise `!=` on the counts answered only 1 and 3 couples |
| Assignment, covering, knapsack, scheduling on time slots | Booleans or small integers, linear sums and `<=` | a 4 x 4 assignment proven optimal in 0.02 s |
| A tour through n places | Boolean arc `x[i][j]`, one arc out and one in per place, an integer order `o[j] >= o[i] + 1 - n * (1 - x[i][j])` against sub-tours | 6, 12, 20, 20 and 30 places, each proven optimal: 12 s at most, 24 s for all five |
| A path through states (puzzles with moves) | enumerate the reachable states in the program, then a Boolean per (step, state) with the linear constraint that each state is followed by one of its successors | a water-jug puzzle: optimum proven in 2 s, where integer amounts per step with products timed out |
| Order of events, positions, permutations when only a solution is needed | `list(n)` with `count == n`, `model.at(array, list[i])`, `model.index(list, value)` | knight's tours on boards 5 to 10: 7 s at most; all-interval series of 5 to 20 numbers: 7 s at most; weak for proofs |
| Choosing groups (social golfers, partitions) | `set(n)` decisions with `model.partition(...)` | 8 schedules of 3 to 8 weeks, 2 to 8 groups and 2 to 6 golfers per group: 12 s at most, where integer group labels timed out on two of them |
| An equation Hexaly cannot satisfy over free integers | (a) a short list of candidates per unknown: `model.at(model.array(candidates), choice)` with `choice` an integer decision (divisors of a product, digit triples of a sum of fractions); (b) a chain: one free decision, every other value an expression of it | a sum of three fractions with distinct digits equal to 1: 20 s with digit triples, free integers with pairwise `!=` timed out; 2 to 4 item prices of a total up to 720 cents whose sum and product agree: 5 s at most with divisors; six charges tied by pair totals: 1 s as a chain from one free charge, free integers timed out |
| Several operations applied in some order | write out the effect of each possible order in the program (a table of straight lines) and let Hexaly pick the order by index | four operations on two unknown ages: 5 s, where integers per step with an order list timed out |

## Add

- **Implied constraints you can derive** shrink the search. For "the first n digits are divisible by n"
  the whole number ends in 0, the fifth digit is 5 and the digits in even places are even, which leaves
  576 candidates of 3.6 million permutations. State the derivation in a comment.
- **Check the statement before changing the formulation.** A model that finds nothing may be unsatisfiable.
  Three formulations of a sixteen-word sum found nothing because each added "no number starts with a
  zero", which the statement does not give; a brute force over the 3.6 million digit assignments in plain
  Python showed the sum has one solution, and it has a zero in a leading place. Dropping the rule solved it
  in 47 s. When a small version has a few million assignments, enumerate it in plain Python first.

## What stalls

| Symptom | Cause | Remedy |
|---|---|---|
| a first solution in seconds, then the search for a second runs to the limit | the solutions are isolated points (a season timetable of nine teams, a quasigroup of order 9, an 8 x 8 still life): a re-solve from the previous solution has no neighbour to move to | none within the limit; one-hot Booleans did not change it for order 9 |
| an optimum that is never proven (`FEASIBLE` at the limit) | an objective with no linear structure: a sum of squares of sums of products of +1/-1 decisions (low autocorrelation, from n = 16), distinct pairwise differences (Golomb ruler, from 8 marks), products of layout counts and sheets (template design) | none; the implied bound `marks[j] - marks[i] >= (j - i)(j - i + 1) / 2` did not close 8 marks. Report the best value as unproven |
| `INFEASIBLE` at the limit on a puzzle that has a solution | free integers under one tight equation, or all-different over many integers | the rows above; for a perfect square packing, a Boolean per (square, corner cell) with every cell covered once did no better than pairwise non-overlap, and neither packed 19 squares into 30 x 30 or the 21 squares of order 112 |
