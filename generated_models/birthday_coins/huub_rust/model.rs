// Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence)
// or a sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
// worth £1 5s 6d. How many half-crowns could he have been given?
fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The instance has no fields: every number below is from the problem statement.
    // How many coins of each kind he was given: a kind may be absent (0), and no kind can
    // number more than the 15 coins.
    let half_crowns = m.new_int_decision(0..=15);
    let shillings = m.new_int_decision(0..=15);
    let sixpences = m.new_int_decision(0..=15);

    // He was given 15 coins.
    m.linear(half_crowns + shillings + sixpences).eq(15).post()?;

    // They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    // shilling 12 and a sixpence 6.
    m.linear(half_crowns * 30 + shillings * 12 + sixpences * 6).eq(306).post()?;

    let mut out = Out::new();
    out.put("half_crowns", half_crowns);
    Ok(out)
}
