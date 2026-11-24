% cell_tower: a clingo model from DCP Rosetta.
%
% A telecom company needs to build a set of cell towers to provide signal coverage for the inhabitants of a
% given city. A number of potential locations where the towers could be built have been identified. The towers
% have a fixed range, and due to budget constraints only a limited number of them can be built. The company
% wishes to provide coverage to the largest percentage of the population possible. The area is split into a set
% of regions, each with a known population. Choose which of the potential locations to build towers on, so
% that as many people as possible are covered.
%
% Save this file as model.lp. Download `cell_tower.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py cell_tower.json
%   python -m clingo model.lp cell_tower_1.lp

% Input: budget(B) holds the budget B; cost(I, C): building a tower at site I costs C; delta(I, J, B): B is 1
% when a tower at site I covers region J and 0 when not; population(J, P): region J has P inhabitants
% (indices are 0-based, as in the data).

site(I) :- cost(I, _).

% built(I): a tower is built at site I
{ built(I) } :- site(I).

% build_tower(I, true) if a tower is built at site I, and false otherwise
build_tower(I, true) :- built(I).
build_tower(I, false) :- site(I), not built(I).

% the total cost of the towers built does not exceed the budget
:- budget(B), #sum { C, I : built(I), cost(I, C) } > B.

% a region is covered when a tower built at a site covers it
covered(J) :- built(I), delta(I, J, 1).

% total_population_covered: the population of the covered regions, which is as large as possible
total_population_covered(T) :- T = #sum { P, J : covered(J), population(J, P) }.
#maximize { T : total_population_covered(T) }.

#show build_tower/2.
#show total_population_covered/1.
