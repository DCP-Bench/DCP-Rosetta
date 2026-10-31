hints.md (coordinator) was used. Attempt 1 failed on convention (no rotation, top below bottom); fixed here:
rotation by a 0/1 `turned`, top = bottom + vertical extent, left/right in 0..W, top/bottom in 0..L.

Performance on the two 16x16 exact tilings: pairwise Reified disjunctions + Diff2 + Cumulative did not
finish in 180 s. What worked: one Boolean per placement (container, orientation, left, bottom) with exact-one
per container and a cell-cover constraint (LinearInt "== 1" per deck cell when areas fill the deck, "<= 1"
otherwise), channelled to left/bottom/turned by LinearInt. Search over the placement Booleans in anchor
order (row, column, container, orientation) with IndomainMax: 8-25 s on the 16x16 instances.

Trap: labelling only turned/left/bottom (placement Booleans labelled afterwards by the runner) gave a first
solution with overlapping containers on the tiling_rotation instance. The channel LinearInts cannot pick a
single placement from left/bottom, and the result was invalid. Put the placement Booleans themselves in
model.search(order, ...).
