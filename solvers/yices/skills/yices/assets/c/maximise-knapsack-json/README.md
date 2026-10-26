# Knapsack from JSON (maximise)

**Problem:** pick items (weight, value) under a capacity to maximise value; the instance is read from a JSON file given as first argument (default `data.json`).
**Shows:** a ragged `conflicts` list (rows of different lengths) read with `cJSON_GetArraySize` per row, reading JSON with cJSON (`-lcjson`), sizes taken from the data, extra keys ignored, maximising by tightening `objective > best` until UNSAT.
**Run:** `cc -std=gnu99 -O2 model.c -o model -lyices -lcjson && ./model data.json`
**Expected:** `Objective: 23 (optimal)`
