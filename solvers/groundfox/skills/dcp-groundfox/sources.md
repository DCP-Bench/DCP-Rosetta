# Sources for `dcp-groundfox`

## Shared

- GroundFOX/CheckFOX repository, README, `docs/FOX_EBNF.md`, `changelog.md`, `examples/` —
  <https://gitlab.kuleuven.be/krr/software/groundfox-checkfox>, version 0.1.2, commit
  f30fb9ce7341425bfb04a19851f6901cc0dbf88d, MPL-2.0, accessed 2026-11-25
- CertiFOX input specification — <https://gitlab.kuleuven.be/krr/software/certifox/-/blob/main/inputSyntax.md>,
  accessed 2026-11-25
- D. Van Caudenberg, A. Ek, C. Cantero, B. Bogaerts, "Towards a Certifying Grounder",
  arXiv:2607.21199 (2026) — <https://arxiv.org/abs/2607.21199>
- python-sat 1.8.dev19 (Glucose 4.2) — <https://pysathq.github.io/>

## FOX

Every form in SKILL.md and interfaces/fox.md was run with groundfox 0.1.2 built with GCC 14
on Debian trixie: the accepted forms ground, the rejected ones give the quoted messages.
