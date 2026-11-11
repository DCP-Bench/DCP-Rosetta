% assignment_costs: a MiniZinc model from DCP Rosetta.
%
% Assign people to 4 tasks with different costs, so that the total cost is minimized.
% Each task must be assigned to exactly one person, but it is not necessary to assign all people to a task.
%
% Save this file as model.mzn. Download `assignment_costs.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py assignment_costs.json
%   minizinc model.mzn assignment_costs_1.json

array[int, int] of int: cost;                       % cost[i,j]: cost of assigning task i to person j

set of int: Tasks = index_set_1of2(cost);           % one index per task
set of int: People = index_set_2of2(cost);          % one index per person

array[Tasks, People] of var bool: x;                % x[i,j]: task i is assigned to person j
var int: objective = sum(i in Tasks, j in People)(cost[i,j] * bool2int(x[i,j]));

% each task is assigned to exactly one person
constraint forall(i in Tasks)(sum(j in People)(bool2int(x[i,j])) = 1);

% each person is assigned to at most one task
constraint forall(j in People)(sum(i in Tasks)(bool2int(x[i,j])) <= 1);

solve minimize objective;
output ["{\"x\": ", showJSON(x), "}"];
