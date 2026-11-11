% csplib_022_bus_driver_scheduling: a MiniZinc model from DCP Rosetta.
%
% This problem requires finding an optimal schedule for bus drivers. Given a set of tasks (pieces of work) to cover and a
% large set of possible shifts, where each shift covers a subset of the tasks, we must select a subset of shifts that
% covers each piece of work exactly once.
%
% The goal is to cover all tasks while minimizing the total number of shifts used. The cost of each shift is considered
% equal.
%
% Save this file as model.mzn. Download `csplib_022_bus_driver_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_022_bus_driver_scheduling.json
%   minizinc model.mzn csplib_022_bus_driver_scheduling_1.json

int: num_work;                                    % the number of pieces of work to cover
int: num_shifts;                                  % the number of possible shifts
set of int: Work = 0..num_work-1;                 % the pieces of work, numbered from 0 in the data
set of int: Shifts = 1..num_shifts;               % the possible shifts

% shifts[s,j]: the j-th piece of work that shift s covers, for j up to shifts_len[s];
% entries past shifts_len[s] are padding and must not be read
array[int, int] of int: shifts;
% shifts_len[s]: the number of pieces of work that shift s covers (created by the conversion)
array[int] of int: shifts_len;

% x[s]: shift s is selected
array[Shifts] of var bool: x;

var int: objective = sum(s in Shifts)(bool2int(x[s]));   % the number of shifts used

% each piece of work is covered by exactly one selected shift
constraint forall(w in Work)(
    sum(s in Shifts)(bool2int(x[s] /\ exists(j in 1..shifts_len[s])(shifts[s, j] = w))) = 1);

solve minimize objective;

output ["{\"x\": ", showJSON(x), "}"];
