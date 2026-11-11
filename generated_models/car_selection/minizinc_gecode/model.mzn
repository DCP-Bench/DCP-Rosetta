% car_selection: a MiniZinc model from DCP Rosetta.
%
% This problem assigns participants to cars to maximize the total number of assignments. Each participant
% may be interested in a subset of the available cars. Each participant is assigned to at most one car, and
% each car is assigned to at most one participant.
%
% Save this file as model.mzn. Download `car_selection.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py car_selection.json
%   minizinc model.mzn car_selection_1.json

% possible_assignments[i,j]: 1 if participant i is interested in car j, 0 otherwise
array[int, int] of int: possible_assignments;

set of int: Participants = index_set_1of2(possible_assignments);
set of int: Cars = index_set_2of2(possible_assignments);

% assignments[i,j]: participant i is assigned to car j
array[Participants, Cars] of var bool: assignments;

% the total number of assignments
var int: objective = sum(i in Participants, j in Cars)(bool2int(assignments[i,j]));

% a participant is assigned only to a car they are interested in
constraint forall(i in Participants, j in Cars)(
    assignments[i,j] -> possible_assignments[i,j] = 1
);

% each participant is assigned to at most one car
constraint forall(i in Participants)(
    sum(j in Cars)(bool2int(assignments[i,j])) <= 1
);

% each car is assigned to at most one participant
constraint forall(j in Cars)(
    sum(i in Participants)(bool2int(assignments[i,j])) <= 1
);

solve maximize objective;

output ["{\"assignments\": ", showJSON(assignments), "}"];
