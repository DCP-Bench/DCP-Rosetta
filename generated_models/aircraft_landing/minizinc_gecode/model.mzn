% aircraft_landing: a MiniZinc model from DCP Rosetta.
%
% The Aircraft Landing Problem involves scheduling the landing of a set of aircraft on a single runway.
% Each aircraft has a specified time window (earliest and latest possible landing time) and a target
% landing time. Penalties are incurred for landing earlier or later than the target time. Additionally, a
% minimum separation time between the landings of any two aircraft must be respected. The aircraft land
% in a fixed sequence. The objective is to determine the exact landing time for each aircraft to minimize
% the total penalty, while respecting all time windows and separation constraints.
%
% Save this file as model.mzn. Download `aircraft_landing.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py aircraft_landing.json
%   minizinc model.mzn aircraft_landing_1.json

array[int] of int: earliest_landing;           % earliest_landing[i]: earliest landing time of aircraft i
array[int] of int: latest_landing;             % latest_landing[i]: latest landing time of aircraft i
array[int] of int: target_landing;             % target_landing[i]: preferred landing time of aircraft i
array[int] of int: penalty_before;             % penalty_before[i]: cost per time unit aircraft i lands early
array[int] of int: penalty_after;              % penalty_after[i]: cost per time unit aircraft i lands late
array[int, int] of int: separation_time;       % separation_time[i,j]: minimum gap from landing i to landing j

set of int: Aircraft = index_set(earliest_landing);

% landing_times[i]: landing time of aircraft i
array[Aircraft] of var int: landing_times;
% earliness[i]: how far before its target aircraft i lands
array[Aircraft] of var 0..max(target_landing): earliness;
% lateness[i]: how far after its target aircraft i lands
array[Aircraft] of var 0..max(latest_landing): lateness;

% each aircraft lands within its time window
constraint forall(i in Aircraft)(landing_times[i] >= earliest_landing[i] /\ landing_times[i] <= latest_landing[i]);

% the earliness of each aircraft is how far its landing is before the target
constraint forall(i in Aircraft)(earliness[i] = max(0, target_landing[i] - landing_times[i]));

% the lateness of each aircraft is how far its landing is after the target
constraint forall(i in Aircraft)(lateness[i] = max(0, landing_times[i] - target_landing[i]));

% the landings follow the fixed sequence (aircraft index order), with the minimum separation between
% any two of them
constraint forall(i, j in Aircraft where i < j)(landing_times[j] - landing_times[i] >= separation_time[i, j]);

% the total penalty for early and late landings
var int: objective = sum(i in Aircraft)(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]);

solve minimize objective;

output ["{\"landing_times\": ", showJSON(landing_times), ", \"total_penalty\": ", showJSON(objective), "}"];
