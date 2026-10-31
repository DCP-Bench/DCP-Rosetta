# conditional-constraints

Reification over integer expressions without `encode_implied`: `b -> x + y <= 4` keeps all 51 solutions, and `b <-> x + y == k` literals.

**Run:** `cargo run --release`
**Expected:** `b -> x + y <= 4: 51 rows`

The helper functions at the top of `src/main.rs` are the same in every example of this skill.
