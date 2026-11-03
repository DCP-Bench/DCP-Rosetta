# jobs_puzzle, attempt 001

- Clue 5 ("Person 0, the chef, and the police officer went golfing together") is read as three different people: the chef and the police officer are neither person 0 nor each other. The brief does not say whether the chef or police officer may be person 0.
- Clues 1 and 4 read "the nurse is not a teacher" as the holder of nurse and the holder of teacher being different people. Since each job has one holder, this is `job[nurse] != job[teacher]`.
- The evaluator accepted two solutions on the single instance, so the model is not checked for uniqueness beyond what the reference accepts.
