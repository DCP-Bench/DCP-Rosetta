// Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence)
// or a sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
// worth £1 5s 6d. How many half-crowns could he have been given?
fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The instance has no fields: every number below is from the problem statement.
    // How many coins of each kind he was given: a kind may be absent (0), and no kind can
    // number more than the 15 coins.
    let half_crowns = IntVar::new(0..=15);
    let shillings = IntVar::new(0..=15);
    let sixpences = IntVar::new(0..=15);

    // He was given 15 coins.
    post(s, iv(&half_crowns) + iv(&shillings) + iv(&sixpences), Comparator::Equal, 15)?;

    // They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    // shilling 12 and a sixpence 6.
    post(
        s,
        scaled(&half_crowns, 30) + scaled(&shillings, 12) + scaled(&sixpences, 6),
        Comparator::Equal,
        306,
    )?;

    let mut out = Out::new();
    out.put("half_crowns", &half_crowns);
    Ok(out)
}
