% cell_tower: a MiniZinc model from DCP Rosetta.
%
% A telecom company needs to build a set of cell towers to provide signal coverage for the inhabitants of a
% given city. A number of potential locations where the towers could be built have been identified. The
% towers have a fixed range, and due to budget constraints only a limited number of them can be built. The
% company wishes to provide coverage to the largest percentage of the population possible. The area is split
% into a set of regions, each of which has a known population. Choose which of the potential locations to
% build cell towers on in order to provide coverage to as many people as possible.
%
% Save this file as model.mzn. Download `cell_tower.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py cell_tower.json
%   minizinc model.mzn cell_tower_1.json

int: budget;                                 % the total cost of the towers that can be built
array[int] of int: cost;                     % cost[s]: the cost of building a tower at site s
% delta[s,r]: 1 if a tower at site s covers region r, 0 otherwise
array[int, int] of int: delta;
array[int] of int: population;               % population[r]: the number of inhabitants of region r

set of int: Sites = index_set(cost);
set of int: Regions = index_set(population);

% build_tower[s]: a tower is built at site s
array[Sites] of var bool: build_tower;

% covered[r]: region r has signal coverage
array[Regions] of var bool: covered;

% the towers built cost no more than the budget
constraint sum(s in Sites)(cost[s] * bool2int(build_tower[s])) <= budget;

% a region is covered exactly when a tower built at a site covering it
constraint forall(r in Regions)(
    covered[r] <-> exists(s in Sites)(build_tower[s] /\ delta[s, r] = 1)
);

% total_population_covered: the number of inhabitants covered by towers
var int: total_population_covered = sum(r in Regions)(population[r] * bool2int(covered[r]));
var int: objective = total_population_covered;

solve maximize objective;

output ["{\"build_tower\": ", showJSON(build_tower), ", \"total_population_covered\": ",
        showJSON(total_population_covered), "}"];
