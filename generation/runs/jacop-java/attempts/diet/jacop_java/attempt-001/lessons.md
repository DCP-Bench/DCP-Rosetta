# Lessons: diet, jacop_java

- The nutrient table (calories, chocolate, sugar, fat per food) is in the problem statement, not the
  instance, so it is written as a constant in the model. The instance gives prices and minimum limits.
- The per-food upper bound (sum of the limits) is a generous bound chosen by hand. It is not proven
  to keep an optimum in every instance; the five instances checked all reach their optimum below it.
