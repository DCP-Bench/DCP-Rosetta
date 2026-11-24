% appointment_scheduling: a MiniZinc model from DCP Rosetta.
%
% Schedule the people into the interview slots based on their free-busy schedules, where m[i,j] is 1 if
% person i is free in slot j. Each person gets exactly one slot in which they are free, and each slot goes
% to exactly one person.
%
% Save this file as model.mzn. Download `appointment_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py appointment_scheduling.json
%   minizinc model.mzn appointment_scheduling_1.json

array[int, int] of int: m;                     % m[i,j]: 1 if person i is free in slot j

set of int: People = index_set_1of2(m);
set of int: Slots = index_set_2of2(m);

% x[i,j]: person i is given slot j
array[People, Slots] of var bool: x;

% each person gets exactly one slot
constraint forall(i in People)(sum(j in Slots)(bool2int(x[i, j])) = 1);

% each slot goes to exactly one person
constraint forall(j in Slots)(sum(i in People)(bool2int(x[i, j])) = 1);

% a person gets a slot only in which they are free
constraint forall(i in People, j in Slots)(x[i, j] -> m[i, j] = 1);

solve satisfy;

output ["{\"x\": ", showJSON(x), "}"];
