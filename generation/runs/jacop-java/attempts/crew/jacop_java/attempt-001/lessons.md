# crew, jacop_java: lessons

- The brief does not say what the columns of `attributes` and `required_crew` mean.
  Read from the data: attributes = [steward, hostess, French, Spanish, German];
  required_crew = [crew size, stewards, hostesses, French, Spanish, German]. Each
  attendant is exactly one of steward or hostess, so the role requirements cannot be
  exact (for example crew 4 with 1 steward and 1 hostess), and they are posted as
  at-least. Language counts are at-least too, matching the instance note.
- The crew size is posted as an exact sum. The rest rule is pairwise: an attendant
  on flight f is off f+1 and f+2.
- Accepted on all 5 instances on the first evaluation.
