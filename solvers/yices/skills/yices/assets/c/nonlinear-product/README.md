# Nonlinear product (QF_NIA)

**Problem:** find x < y, both above 1, with x * y = 91.
**Shows:** the default context rejects a product of two variables when it is asserted (not when the term is built); `yices_default_config_for_logic(cfg, "QF_NIA")` selects the MCSAT solver; `yices_has_mcsat()`.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices && ./model`
**Expected:** `does not support non-linear arithmetic`
**Expected:** `x=7 y=13`
