# Lessons: ages_of_the_sons, attempt 1

- The puzzle has no instance fields, so the only instance is the example and nothing checks the
  constants. The age triples come from the product 36, which is a constant of the statement.
- The clues are epistemic. The model writes them as constraints over a candidate index: "some other
  candidate has the same sum" (clue 2, an existential), and "every other candidate with the same
  sum has a tie for oldest" (clue 3, a universal, posted per candidate as reified implications).
- The solver returns 9, 2, 2 with status complete.
