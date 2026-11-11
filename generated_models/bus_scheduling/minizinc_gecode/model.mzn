% bus_scheduling: a MiniZinc model from DCP Rosetta.
%
% Progress City is considering a mass-transit bus system to reduce in-city driving. The goal is to
% determine the minimum number of buses required to meet the transportation needs throughout the day.
% The demand for buses is approximated as constant over successive 4-hour intervals. Each bus can operate
% only 8 successive hours a day, so a bus that starts in one interval also works in the next one. The day
% is cyclic: the first interval follows the last. The number of buses available in each 4-hour interval,
% those starting in it and those that started in the interval before, meets the demand for that interval.
%
% Save this file as model.mzn. Download `bus_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py bus_scheduling.json
%   minizinc model.mzn bus_scheduling_1.json

include "globals.mzn";

array[int] of int: demands;                       % demands[s]: the buses needed in interval s
set of int: Intervals = index_set(demands);       % the 4-hour intervals of the day, in order
int: num_intervals = card(Intervals);

% the interval before interval s, the first interval following the last
function int: previous(int: s) = (s + num_intervals - 2) mod num_intervals + 1;

% x[s]: the number of buses that start in interval s (at most max(demands): an optimal plan never needs more, implied bound)
array[Intervals] of var 0..max(demands): x;

% in each interval, the buses that start in it and those that started in the interval before meet its demand
constraint forall(s in Intervals)(x[s] + x[previous(s)] >= demands[s]);

% the fewest buses
var int: objective = sum(x);

solve minimize objective;
output ["{\"x\": ", showJSON(x), "}"];
