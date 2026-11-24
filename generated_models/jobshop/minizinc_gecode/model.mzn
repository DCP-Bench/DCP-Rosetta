% jobshop: a MiniZinc model from DCP Rosetta.
%
% One common scheduling problem is the job shop, in which multiple jobs are processed on several machines.
% Each job consists of a sequence of tasks, which must be performed in a given order, and each task must be
% processed on a specific machine. The problem is to schedule the tasks on the machines so as to minimize the
% length of the schedule, the time it takes for all the jobs to be completed. The constraints are: no task
% for a job can be started until the previous task for that job is completed; a machine can only work on one
% task at a time; and a task, once started, must run to completion.
%
% Save this file as model.mzn. Download `jobshop.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py jobshop.json
%   minizinc model.mzn jobshop_1.json

include "globals.mzn";

% jobs_data[j,k,1] is the machine of task k of job j, and jobs_data[j,k,2] its duration
array[int, int, int] of int: jobs_data;
% jobs_data_len[j] is the number of tasks of job j; the rows are padded after that
array[int] of int: jobs_data_len;

set of int: Jobs = index_set(jobs_data_len);      % the jobs
int: max_tasks = max(jobs_data_len);              % the largest number of tasks in a job
set of int: Tasks = 1..max_tasks;                 % task positions within a job, in order
int: num_machines = max([jobs_data[j, k, 1] | j in Jobs, k in 1..jobs_data_len[j]]) + 1;
set of int: Machines = 0..num_machines - 1;       % machines are numbered from 0

% no schedule is longer than running all tasks one after another
int: horizon = sum([jobs_data[j, k, 2] | j in Jobs, k in 1..jobs_data_len[j]]);

% start[j,k]: the start time of task k of job j (unused positions stay at 0)
array[Jobs, Tasks] of var 0..horizon: start;
var 0..horizon: makespan;                         % the time at which all jobs are completed
var int: objective = makespan;

% unused positions after the last task of a job are fixed to 0
constraint forall(j in Jobs, k in Tasks where k > jobs_data_len[j])(start[j, k] = 0);

% implied bounds, not part of the problem: a task cannot start before the earlier tasks of its job are done, and must leave room
% for the later tasks of its job before the horizon
constraint forall(j in Jobs, k in Tasks where k <= jobs_data_len[j])(
    start[j, k] >= sum(l in 1..k - 1)(jobs_data[j, l, 2]) /\
    start[j, k] + sum(l in k..jobs_data_len[j])(jobs_data[j, l, 2]) <= horizon);

% implied bounds, not part of the problem: the makespan is at least the total work of every job and of every machine
constraint forall(j in Jobs)(
    makespan >= sum(k in 1..jobs_data_len[j])(jobs_data[j, k, 2]));
constraint forall(m in Machines)(
    makespan >= sum([jobs_data[j, k, 2] | j in Jobs, k in 1..jobs_data_len[j] where jobs_data[j, k, 1] = m]));

% no task of a job can start until the previous task of that job is completed
constraint forall(j in Jobs, k in Tasks where k < jobs_data_len[j])(
    start[j, k] + jobs_data[j, k, 2] <= start[j, k + 1]);

% a machine can only work on one task at a time, and a task runs to completion
constraint forall(m in Machines)(
    disjunctive([start[j, k] | j in Jobs, k in Tasks where k <= jobs_data_len[j] /\ jobs_data[j, k, 1] = m],
                [jobs_data[j, k, 2] | j in Jobs, k in Tasks where k <= jobs_data_len[j] /\ jobs_data[j, k, 1] = m]));

% the makespan is no earlier than the end of the last task of every job
constraint forall(j in Jobs)(
    makespan >= start[j, jobs_data_len[j]] + jobs_data[j, jobs_data_len[j], 2]);

solve minimize objective;

output ["{\"makespan\": ", showJSON(makespan), "}"];
