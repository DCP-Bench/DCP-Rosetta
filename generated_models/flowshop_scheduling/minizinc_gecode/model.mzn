% flowshop_scheduling: a MiniZinc model from DCP Rosetta.
%
% A set of jobs need to be processed on a set of machines in series. All jobs have the same processing
% order through all the machines, from machine 1 to machine M. Each machine can work in
% parallel. The time required to process job j on machine m is process_time[j,m]. Find a sequence of the
% jobs that minimizes the makespan: the time when all jobs have been processed.
%
% Save this file as model.mzn. Download `flowshop_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py flowshop_scheduling.json
%   minizinc model.mzn flowshop_scheduling_1.json

include "globals.mzn";

array[int,int] of int: process_time;                % process_time[j,m]: time job j needs on machine m
set of int: Jobs = index_set_1of2(process_time);     % one index per job
set of int: Machines = index_set_2of2(process_time); % machines, visited in increasing index order

% no schedule needs more time than all the work done one job after another
int: horizon = sum(j in Jobs, m in Machines)(process_time[j,m]);

% sequence[k]: the job processed in position k of the sequence
array[Jobs] of var Jobs: sequence;

% every job appears exactly once in the sequence
constraint all_different(sequence);

% start[k,m], finish[k,m]: start and completion time on machine m of the job in position k
array[Jobs, Machines] of var 0..horizon: start;
array[Jobs, Machines] of var 0..horizon: finish;

% processing a job on a machine takes its processing time there
constraint forall(k in Jobs, m in Machines)(finish[k,m] = start[k,m] + process_time[sequence[k],m]);

% a job starts on a machine as soon as it has arrived from the machine before and the previous job of
% the sequence has left this machine, so each sequence gives one schedule
constraint forall(k in Jobs, m in Machines)(
    start[k,m] = if k > 1 /\ m > 1 then max(finish[k,m-1], finish[k-1,m])
                 elseif m > 1 then finish[k,m-1]
                 elseif k > 1 then finish[k-1,m]
                 else 0 endif);

% the makespan is the time when the last job finishes on the last machine
var 0..horizon: makespan = max(k in Jobs)(finish[k, max(Machines)]);

var int: objective = makespan;

solve minimize objective;

output ["{\"makespan\": ", showJSON(makespan), "}"];
