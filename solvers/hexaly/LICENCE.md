# Hexaly licence

## What you need

A Hexaly Optimizer licence file, `license.dat`. A free trial or an academic licence is
enough to build and debug the models here; the commercial licence is the upgrade if the
results are to be used beyond the terms of a trial or academic licence.

## Get it

Register at https://www.hexaly.com/registration for a free trial or an academic licence.
The registration page is the place to read the current terms.

## What you receive

A file named `license.dat`. It is a file, not a folder, and it is never committed.

## Store it

Keep it outside the repository, for example `~/.config/dcp-rosetta/licences/hexaly/license.dat`,
with `chmod 600`.

## Configure

```sh
python -m evaluation.licences set hexaly ~/.config/dcp-rosetta/licences/hexaly/license.dat
```

This records only the path (in `.dcp-licences.json`, per checkout); the file is never read.

## Verify

```sh
python -m evaluation.licences check hexaly
```

This checks the file, then solves the pilot model with it.

## How the evaluator uses it

The integration (`solvers/hexaly/python/metadata.json`) declares the licence with
`HX_LICENSE_PATH`. The evaluator binds the file read-only at `/run/licence/license.dat` and
points `HX_LICENSE_PATH` at it for each run. The image holds no licence.

Hexaly's own messages, for reference:

- missing licence: `Cannot open file [/opt/hexaly_15_0/license.dat]`
- expired licence: `This license is no longer valid. Please check its expiration date.`

Both are reported as `licence_unavailable`, never as a model's failure.

`HX_LICENSE_PATH` names the file itself. Set to its folder, Hexaly fails with
`Property 'LICENSE_KEY' is missing`.

## Terms

Trial and academic licences are for evaluation and academic use. Check the terms on the
registration page before publishing benchmark results obtained with one.
