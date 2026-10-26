# Adding an interface to a solver skill

A solver has one skill whatever the number of language bindings. Use this when the
target binding's solver already has a skill: a shared one (`interfaces/` present) or an
older flat one written for a single binding (`<solver>-<language>/`, everything in
`SKILL.md`). The layout and the file templates are in [the template](skill-template.md).

## 1. Make the skill shared (flat skill only)

A flat skill is first turned into the shared layout, with its current binding as the only
interface, before anything new is added:

1. Create `<solver>/` (named after the solver only) and move the bundle into it.
2. Sort every section of the old `SKILL.md`:

   | Content | Goes to |
   |---|---|
   | what the solver is, its concepts, which global constraints exist, status meanings, search, enumeration strategy, solver-level issues | `SKILL.md` |
   | install, quick start, exact calls, reading data, status constants, parameter names, enumeration code, issues with that binding's syntax or packaging | `interfaces/<interface>.md` |
   | runnable examples | `assets/<interface>/` (fix the links) |
   | references specific to the binding | `references/<interface>-<name>` |

3. Add the interface table, set `name`, `description` and `metadata.interfaces`, rename
   `evals/evals.json`'s `skill_name` and `expected_skill`, and split `sources.md` into a
   shared section and a section per interface.
4. Nothing may be lost: diff the old and new text, and run the examples
   (`check_assets.py <skill> --interface <interface>`).

When two flat skills of the same solver already exist, do this for the better-tested one,
then add the other as in step 2, using its text as the draft for the new interface file.

## 2. Add the new interface

1. Write `interfaces/<interface>.md` and `assets/<interface>/` from the template, with your
   research and probes for this binding.
2. Re-read every shared claim in `SKILL.md` against the new binding and run the ones in
   doubt. A claim that does not hold for it moves out of the shared text: into a row of the
   interface table when a reader choosing a binding needs to know, otherwise into the
   interface files where it holds. Never weaken the shared text to "usually".
3. Add the new column to the interface table, and fill each feature row from a run or the
   binding's documentation, cited in `sources.md`.
4. Add the binding to `description`, `compatibility` and `metadata.interfaces`, and add its
   evals.

## 3. Verify

A change to the shared text changes what every binding's reader is taught, so:

- `check_assets.py <skill> --interface <i>` passes for **every** interface, each with its own
  `--image` when the solver lives in containers.
- `generation.skills validate --project`, `rosetta-mentions`, `skills-ref validate`.
- The toy-problem round passes for the new interface. For the existing interfaces, rerun the
  round when shared text was rewritten (not only moved); otherwise their asset checks suffice.
- One standalone review of the whole skill, which also checks shared claims against every
  interface file.

Then point every integration of the solver at the skill (`skill` and `interface` in its
`metadata.json`) and remove the flat bundles that were merged.
