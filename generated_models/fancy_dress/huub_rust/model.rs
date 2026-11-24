// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.

// A Boolean decision as a formula.
fn atom(b: View<bool>) -> BoolFormula {
    BoolFormula::Atom(b)
}

// "if `cond` then `then`, or he pays the fee `fee`" as a formula.
fn rule_or_fee(cond: BoolFormula, then: BoolFormula, fee: View<bool>) -> BoolFormula {
    BoolFormula::Or(vec![BoolFormula::Implies(Box::new(cond), Box::new(then)), atom(fee)])
}

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The instance has no fields: every number below is from the problem statement.
    let t = m.new_bool_decision(); // he wears a green tie
    let h = m.new_bool_decision(); // he wears a green hat
    let r = m.new_bool_decision(); // he wears a green shirt
    let s = m.new_bool_decision(); // he wears green socks
    let n = m.new_bool_decision(); // he pays the entrance fee

    // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    // rule holds or he pays.
    // Rule 1: if someone wears a green tie he has to wear a green shirt.
    m.proposition(rule_or_fee(atom(t), atom(r), n)).post()?;
    // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    // a green hat.
    m.proposition(rule_or_fee(
        BoolFormula::Or(vec![atom(s), atom(r)]),
        BoolFormula::Or(vec![atom(t), atom(h)]),
        n,
    ))
    .post()?;
    // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    // must wear a green tie.
    m.proposition(rule_or_fee(
        BoolFormula::Or(vec![atom(r), atom(h), BoolFormula::Not(Box::new(atom(s)))]),
        atom(t),
        n,
    ))
    .post()?;

    // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    let cost = m.new_int_decision(0..=10 + 2 + 12 + 11);
    m.linear(t * 10 + h * 2 + s * 12 + n * 11).eq(cost).post()?;

    let mut out = Out::new();
    out.put("t", t).put("h", h).put("r", r).put("s", s).put("n", n);
    out.minimise(cost);
    Ok(out)
}
