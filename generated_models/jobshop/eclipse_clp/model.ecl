% jobshop: an ECLiPSe model from DCP Rosetta.
%
% In a job shop, several jobs are each a sequence of tasks, performed in a given order, and each task
% must be processed on a specific machine. Schedule the tasks on the machines so as to minimise the
% makespan, the time it takes for all the jobs to be completed. No task for a job can start until the
% previous task of that job is completed, a machine works on one task at a time, and a task once
% started runs to completion.
%
% Save this file as model.ecl. Download `jobshop.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py jobshop.json
%   eclipse -b model.ecl -e "run('jobshop_1.dat'), halt"

:- lib(ic).
:- lib(ic_edge_finder3).
:- lib(listut).

% The data field jobs_data is the list of jobs; each job is the list of its tasks in order, and each
% task is [Machine, Duration], with machines numbered from 0.
model(Data, Vars, [makespan-Makespan], min(Makespan)) :-
    memberchk(jobs_data-Jobs, Data),
    total_duration(Jobs, 0, Horizon),      % no task can start after all the work is done
    % each task gets a start time, task(Machine, Start, Duration), with the tasks of a job in a list
    ( foreach(Job, Jobs), foreach(Tasks, JobTasks), param(Horizon) do
        job_tasks(Job, Horizon, Tasks)
    ),
    % each task of a job starts after the previous task of that job has completed
    ( foreach(Tasks, JobTasks) do
        chain(Tasks)
    ),
    flatten(JobTasks, AllTasks),
    % the makespan is at least the completion time of every task
    Makespan :: 0..Horizon,
    ( foreach(task(_, S, D), AllTasks), param(Makespan) do
        S + D #=< Makespan
    ),
    % a machine works on one task at a time
    max_machine(AllTasks, -1, MaxMachine),
    ( for(M, 0, MaxMachine), param(AllTasks) do
        machine_no_overlap(M, AllTasks)
    ),
    ( foreach(task(_, S, _), AllTasks), foreach(S, Starts) do
        true
    ),
    append(Starts, [Makespan], Vars).

% labelling: first-fail over the start times, then the makespan
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% total_duration(Jobs, H0, H): H is H0 plus the durations of all tasks of all jobs
total_duration([], H, H).
total_duration([Job | Jobs], H0, H) :-
    job_duration(Job, H0, H1),
    total_duration(Jobs, H1, H).

job_duration([], H, H).
job_duration([[_, D] | Tasks], H0, H) :-
    H1 is H0 + D,
    job_duration(Tasks, H1, H).

% job_tasks(Job, Horizon, Tasks): one task(Machine, Start, Duration) per task of the job
job_tasks([], _, []).
job_tasks([[M, D] | Rest], Horizon, [task(M, S, D) | Ts]) :-
    S :: 0..Horizon,
    job_tasks(Rest, Horizon, Ts).

% a task ends before the next task of its job starts
chain([]).
chain([_]).
chain([task(_, S1, D1), task(M2, S2, D2) | Rest]) :-
    S1 + D1 #=< S2,
    chain([task(M2, S2, D2) | Rest]).

% the largest machine number used by the tasks
max_machine([], Max, Max).
max_machine([task(M, _, _) | Ts], Max0, Max) :-
    Max1 is max(Max0, M),
    max_machine(Ts, Max1, Max).

% the tasks on machine M do not overlap in time
machine_no_overlap(M, AllTasks) :-
    on_machine(M, AllTasks, Starts, Durations),
    (   Starts == [] -> true ; disjunctive(Starts, Durations) ).

% Starts and Durations of the tasks that use machine M
on_machine(_, [], [], []).
on_machine(M, [task(M1, S, D) | Ts], Starts, Durations) :-
    (   M1 == M
    ->  Starts = [S | Starts1], Durations = [D | Durations1]
    ;   Starts = Starts1, Durations = Durations1
    ),
    on_machine(M, Ts, Starts1, Durations1).

:- lib(branch_and_bound).

run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
