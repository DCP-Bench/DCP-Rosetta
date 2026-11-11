% resource_constrained_project_scheduling: a MiniZinc model from DCP Rosetta.
%
% The resource-constrained project scheduling problem involves scheduling a set of jobs, each with a
% specific duration and resource requirement, such that the total project duration (makespan) is
% minimized. Each job may have precedence constraints, meaning certain jobs must be completed before
% others can start. Additionally, there are multiple types of resources, each with a limited capacity that
% must not be exceeded at any time. Given the durations of the jobs, their resource requirements, the
% capacities of the resources, and the precedence constraints between the jobs, determine the start times
% of the jobs that minimize the makespan while satisfying all constraints.
%
% Save this file as model.mzn. Download `resource_constrained_project_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py resource_constrained_project_scheduling.json
%   minizinc model.mzn resource_constrained_project_scheduling_1.json

include "globals.mzn";

array[int] of int: durations_data;                  % durations_data[j]: duration of job j
array[int,int] of int: resource_needs_data;         % resource_needs_data[j,r]: amount of resource r job j needs
array[int] of int: resource_capacities_data;        % resource_capacities_data[r]: capacity of resource r
array[int,int] of int: successors_link_data;        % [k,1] must finish before [k,2] starts (jobs counted from 0)

set of int: Jobs = index_set(durations_data);
set of int: Resources = index_set(resource_capacities_data);
set of int: Links = index_set_1of2(successors_link_data);
int: horizon = sum(durations_data);                 % a schedule that runs one job at a time is never longer

% start_time[j]: the time at which job j starts (counted from 0)
array[Jobs] of var 0..horizon: start_time;

% the project's duration: the latest finishing time of any job, to be minimized
var int: objective = max(j in Jobs)(start_time[j] + durations_data[j]);

% a job starts only after each of its predecessors has finished
% (the data counts jobs from 0, so job j of the data is position j + 1 here)
constraint forall(k in Links)(
    start_time[successors_link_data[k,2] + 1] >= start_time[successors_link_data[k,1] + 1] + durations_data[successors_link_data[k,1] + 1]);

% at any time the jobs in progress need no more of each resource than its capacity
constraint forall(r in Resources)(
    cumulative(start_time, durations_data, [resource_needs_data[j,r] | j in Jobs], resource_capacities_data[r]));

solve minimize objective;

output ["{\"start_time\": ", showJSON(start_time), "}"];
