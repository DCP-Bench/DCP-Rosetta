% csplib_044_steiner: a MiniZinc model from DCP Rosetta.
%
% The ternary Steiner problem of order n consists of finding a set of n * (n-1) / 6 triples of distinct
% integer elements in {1, ..., n} such that any two triples have at most one common element. It is a
% hypergraph problem from combinatorial mathematics, where n modulo 6 has to be equal to 1 or 3. This is
% a particular case of the more general Steiner system.
%
% Save this file as model.mzn. Download `csplib_044_steiner.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_044_steiner.json
%   minizinc model.mzn csplib_044_steiner_1.json

int: n;                                          % the order of the Steiner system

set of int: Elements = 1..n;                     % the elements
set of int: Triples = 1..n * (n - 1) div 6;      % the triples, n * (n-1) / 6 of them

% sets[i,j]: element j is in triple i
array[Triples, Elements] of var bool: sets;

% the ternary Steiner system exists only when n is 1 or 3 modulo 6
constraint n mod 6 = 1 \/ n mod 6 = 3;

% each triple consists of three distinct elements
constraint forall(i in Triples)(sum(j in Elements)(bool2int(sets[i, j])) = 3);

% any two triples have at most one common element
constraint forall(i, k in Triples where i < k)(sum(j in Elements)(bool2int(sets[i, j] /\ sets[k, j])) <= 1);

solve satisfy;
output ["{\"sets\": ", showJSON(sets), "}"];
