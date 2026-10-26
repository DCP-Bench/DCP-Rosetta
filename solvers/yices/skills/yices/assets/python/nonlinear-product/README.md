# Nonlinear product (QF_NIA)

**Problem:** integers a < b with a + b = 13, maximise a*b subject to a*b <= 50.
**Shows:** a product of two terms is rejected by the default (linear) context, accepted under `QF_NIA`; maximise by tightening.
**Run:** `python model.py`
**Expected:** `does not support non-linear arithmetic`
**Expected:** `Maximum product: a=6 b=7 a*b=42`
