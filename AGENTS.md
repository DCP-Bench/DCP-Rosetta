# AGENTS.md

## Workflow

- For each new feature or bug fix, always create a new branch and start coding there.
- Make appropriate commits on that branch, but never push — the user handles all pushing.
- Group a batch of related work into one commit rather than committing each file or each
  generated model on its own, and say in the message what the batch carries.
- After coding is done, the user and the agent review whether the request is done.

## The dataset

`bench/` is the DCP-Bench Open repository, checked out as a git submodule pinned to
one commit. The problems are under `bench/dataset/` and their sources in
`bench/SOURCES.md`. Change it only through `skills/instance-curator`: a dataset change
is a commit inside `bench/`, followed by a commit here that moves the pointer.

## Writing models for this benchmark

*Rosetta* is this repository's model collection and the machinery that writes and checks
it (see the README). Skills in `skills/` work only here; the solver skills must work
anywhere, and are mirrored to the public `DCP-Bench/skills` repository. A solver has one
folder `solvers/<solver>/`: its standalone skill under `skills/dcp-<name>/` (the `dcp-`
prefix keeps it apart from upstream skills of the same name), shared by its language bindings, with an
`interfaces/<interface>.md` (or an `interfaces/<interface>/` folder entered through its
`README.md`) per binding; and one integration folder per binding, `<interface>/`, with id
`<solver>_<interface>` and its own `Dockerfile`, runner, `CONTRACT.md` and readiness record.
Each integration is built, certified and modelled for on its own. Every integration is nested
this way; the evaluator still falls back to a flat `solvers/<id>/` for an id it cannot find.

Follow `skills/model-generator`, which runs a
campaign end to end, and `skills/solver-setup` for adding a framework/solver.
Follow `skills/instance-curator` to add instances to existing problems. A generated model should be kept only when the evaluator accepts it.

`python -m generation.brief PROBLEM` prints what a model has to satisfy: the problem
description, the declared output names with their shapes, the objective direction, and
every instance field with its shape. Modelling starts blind, from the brief, the
contracts and the solver skill, without the reference (see `skills/model-generator`). `python -m generation.next_work` says what is left, and withholds pairs whose
instance shape an integration cannot bind at all.

