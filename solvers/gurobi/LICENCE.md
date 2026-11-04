# Gurobi licence

Without a licence, `gurobipy_python` runs on the licence bundled with the gurobipy wheel.
That licence stops at 2000 variables and 2000 linear constraints (200 with quadratic
terms), and the evaluator reports a larger model as `unsupported_capability`. A full
licence lifts the limit. Only a **token-server** licence works here. Each run is a container
with no network and no stable host identity, which rules out the others:

| Licence | Works in the evaluator? |
|---|---|
| Wheel's size-limited licence | yes, by default |
| Token server (floating licence, `TOKENSERVER=` in `gurobi.lic`) | yes, relayed to the container |
| Academic named-user (`grbgetkey`, `HOSTID=` in `gurobi.lic`) | no: `HostID mismatch … hostid is 0` |
| Web License Service (WLS) | no: it needs internet while running |

## Get it

Your institution's token server is run by its IT or research group: ask them for the
server name. The client licence file is one line, sometimes with a port:

```
TOKENSERVER=<server name>
```

The server must run a Gurobi version at least as new as the image's gurobipy (see
`python/CONTRACT.md`, *Environment*), and it has to be reachable from the machine that
runs the evaluator. That usually means being on the institution's network.

## Configure

```sh
mkdir -p ~/.config/dcp-rosetta/licences/gurobi
# write the TOKENSERVER line into ~/.config/dcp-rosetta/licences/gurobi/gurobi.lic
chmod 600 ~/.config/dcp-rosetta/licences/gurobi/gurobi.lic
python -m evaluation.licences set gurobi ~/.config/dcp-rosetta/licences/gurobi/gurobi.lic
python -m evaluation.licences check gurobi
```

Configure it only on machines that can reach the server. Elsewhere, leave it unset and
runs fall back to the wheel's licence. A configured server that can't be reached makes
every run `licence_unavailable`.

## Terms

Gurobi's licence terms, and your institution's, govern use and any publication of
benchmark results. Each run holds one token while the solver works, and gives it back on
exit.
