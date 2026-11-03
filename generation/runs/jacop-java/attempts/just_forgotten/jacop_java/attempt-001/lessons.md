# just_forgotten, attempt 001

- Process note: the modeller opened `bench/dataset/just_forgotten/just_forgotten.json` to read the
  instance sizes. Its `note` fields for `json:2` and `json:3` state the account numbers. Those values
  were not used: the model takes `sets`, `num_correct_digits` and the set length from the instance
  and posts only the constraints from the description. The notes are a dataset issue to report.
- Non-obvious: "exactly k digits in their correct position" is modelled as a per-set sum of
  `Reified(XeqC(x[i], set[i]))` booleans equal to k.
