% jobshop: a SWI-Prolog model from DCP Rosetta.
%
% In the job shop, several jobs are processed on several machines. Each job consists of a sequence of tasks, which
% must be performed in the given order, and each task must be processed on a specific machine. The problem is to
% schedule the tasks on the machines so as to minimise the length of the schedule, the time it takes for all the
% jobs to be completed. No task of a job starts before the previous task of that job is completed, a machine works
% on one task at a time, and a task, once started, runs to completion. Find the optimal makespan, the total time
% taken to complete all jobs.
%
% Save this file as model.pl. Download `jobshop.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('jobshop.json')" -t halt model.pl
%
% Data fields: jobs_data (the jobs, indexed from 0; each job is its list of tasks in order, and each task is the
% pair [machine, duration] with the machine and the duration of the task).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(http/json)).

model(Instance, Vars, [makespan-Makespan], min(Makespan)) :-
    Jobs = Instance.jobs_data,
    append(Jobs, Tasks),
    maplist(task_duration, Tasks, Durations),
    sum_list(Durations, Horizon),          % no schedule is longer than all the tasks run one after another
    % StartLists[J][K] is the start time of task K of job J
    maplist(job_starts(Horizon), Jobs, StartLists),
    Vars = StartLists,
    % the tasks of each job run one after another, in their order
    maplist(job_order, Jobs, StartLists),
    append(StartLists, Starts),
    maplist(make_record, Tasks, Starts, Records),
    % the makespan is at least the end of every task
    Makespan in 0..Horizon,
    maplist(ends_before(Makespan), Records),
    % a machine works on one task at a time
    maplist(task_machine, Tasks, Machines),
    sort(Machines, MachineIds),
    maplist(machine_one_at_a_time(Records), MachineIds).

% task_machine(+Task, -Machine) and task_duration(+Task, -Duration): the two fields of a task [machine, duration]
task_machine([Machine, _], Machine).
task_duration([_, Duration], Duration).

% job_starts(+Horizon, +Job, -Starts): one start time for each task of the job, within the horizon
job_starts(Horizon, Job, Starts) :-
    length(Job, K),
    length(Starts, K),
    Starts ins 0..Horizon.

% job_order(+Tasks, +Starts): each task ends before the next task of the job starts
job_order([_], [_]).
job_order([[_, Duration]|[Next|Rest]], [Start, NextStart|Starts]) :-
    Start + Duration #=< NextStart,
    job_order([Next|Rest], [NextStart|Starts]).

% make_record(+Task, +Start, -Record): a task with its machine, duration and start time
make_record([Machine, Duration], Start, record(Machine, Duration, Start)).

% ends_before(+Makespan, +Record): the task ends no later than the makespan
ends_before(Makespan, record(_, Duration, Start)) :-
    Start + Duration #=< Makespan.

% machine_one_at_a_time(+Records, +Machine): the tasks on the machine do not overlap in time
machine_one_at_a_time(Records, Machine) :-
    include(on_machine(Machine), Records, Here),
    no_overlap(Here).

on_machine(Machine, record(Machine, _, _)).

% no_overlap(+Records): every pair of tasks is one before the other
no_overlap([]).
no_overlap([Record|Records]) :-
    maplist(apart(Record), Records),
    no_overlap(Records).

% apart(+Record1, +Record2): one task ends before the other one starts
apart(record(_, Duration1, Start1), record(_, Duration2, Start2)) :-
    (Start1 + Duration1 #=< Start2) #\/ (Start2 + Duration2 #=< Start1).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
