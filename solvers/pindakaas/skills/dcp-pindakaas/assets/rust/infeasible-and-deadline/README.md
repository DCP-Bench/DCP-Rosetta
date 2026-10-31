# infeasible-and-deadline

A contradiction found while encoding (`Err`), one found by search (empty result), and a 2 s deadline through the terminate callback.

**Run:** `cargo run --release`
**Expected:** `3 different values in 0..=1: 0 rows`
**Expected:** `interrupted = true`

The helper functions at the top of `src/main.rs` are the same in every example of this skill.
