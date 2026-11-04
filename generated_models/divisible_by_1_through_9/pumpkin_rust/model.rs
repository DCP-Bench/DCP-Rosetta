// Divisible by 1 through 9: find a ten-digit number that uses each digit 0 to 9 exactly
// once and where, for every n, the number formed by its first n digits is divisible by n.
// The statement fixes all the data (ten digits, divisors 1 to 10), so the instance has no
// fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n_digits: usize = 10;

    // digits[i]: the digit at position i of the number, read from left to right
    let digits: Vec<Var> = (0..n_digits).map(|_| solver.new_bounded_integer(0, 9)).collect();

    // Each of the digits 0 to 9 is used exactly once.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(digits.clone(), tag)).post();

    // The number formed by the first n digits is divisible by n: it is n times a whole
    // number, the quotient.
    // That number is the sum of digits[j] * 10^(n-1-j), which for n = 10 is above
    // i32::MAX, the largest Pumpkin integer. Replacing each place value 10^(n-1-j) by its
    // remainder modulo n leaves the remainder of the sum modulo n unchanged and keeps the
    // sum below 1000, so the divisibility is the linear equation sum - n * quotient = 0.
    // A digit whose place value is a multiple of n adds nothing to the remainder and is
    // left out of the sum: Pumpkin cannot scale a variable by 0.
    for n in 1..=n_digits {
        let place_values: Vec<i32> = (0..n)
            .map(|j| (10i64.pow((n - 1 - j) as u32) % n as i64) as i32)
            .collect();
        let largest_sum: i32 = place_values.iter().map(|c| 9 * c).sum();
        let quotient = solver.new_bounded_integer(0, largest_sum / n as i32);
        let mut terms: Vec<Term> = (0..n)
            .filter(|&j| place_values[j] != 0)
            .map(|j| digits[j].scaled(place_values[j]))
            .collect();
        terms.push(quotient.scaled(-(n as i32)));
        let tag = solver.new_constraint_tag();
        solver.add_constraint(pumpkin_solver::equals(terms, 0, tag)).post();
    }

    let mut m = Model::new();
    m.put("digits", digits);
    m
}
