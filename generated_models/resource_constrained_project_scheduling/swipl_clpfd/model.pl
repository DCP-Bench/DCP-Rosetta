% resource_constrained_project_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% The resource-constrained project scheduling problem involves scheduling a set of jobs, each with a specific duration
% and resource requirement, such that the total project duration (makespan) is minimized. Each job may have precedence
% constraints, meaning certain jobs must be completed before others can start. Additionally, there are multiple types
% of resources, each with a limited capacity that must not be exceeded at any time. Given the durations of the jobs,
% their resource requirements, the capacities of the resources, and the precedence constraints between the jobs,
% determine the start times of the jobs that minimize the makespan while satisfying all constraints.
%
% Save this file as model.pl. Download `resource_constrained_project_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('resource_constrained_project_scheduling.json')" -t halt model.pl
%
% Data fields: durations_data (the duration of each job), resource_capacities_data (the capacity of each resource),
% resource_needs_data (the amount of each resource that each job needs, one list per job), successors_link_data (each
% pair [I, J] says that job I must be completed before job J starts), lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(http/json)).

model(Instance, Starts-Makespan, [start_time-Starts], min(Makespan)) :-
    Durations = Instance.durations_data,
    Capacities = Instance.resource_capacities_data,
    Needs = Instance.resource_needs_data,
    Links = Instance.successors_link_data,
    length(Durations, N),
    length(Capacities, R),
    Last is R - 1,
    numlist(0, Last, Resources),
    sum_list(Durations, Horizon),
    % the start time of each job is between 0 and the sum of all durations
    length(Starts, N),
    Starts ins 0..Horizon,
    % the end of each job is its start plus its duration
    length(Ends, N),
    maplist(end_time, Starts, Durations, Ends),
    % each job starts only once every job that must precede it is completed
    maplist(precedence(Starts, Ends), Links),
    % the usage of each resource never exceeds its capacity at any time
    maplist(resource_limit(Starts, Durations, Ends, Needs, Capacities), Resources),
    % the makespan is at least the end of every job, and it is what is minimised
    Makespan in 0..Horizon,
    maplist(finish_by(Makespan), Ends).

% end_time(+S, +D, -E): a job starting at S with duration D ends at E
end_time(S, D, E) :- E #= S + D.

% finish_by(+Makespan, +E): a job ending at E finishes no later than the makespan
finish_by(Makespan, E) :- E #=< Makespan.

% precedence(+Starts, +Ends, +Link): job I, the first of the pair, is completed before job J, the second, starts
precedence(Starts, Ends, [I, J]) :-
    nth0(I, Ends, EndI),
    nth0(J, Starts, StartJ),
    StartJ #>= EndI.

% resource_limit(+Starts, +Durations, +Ends, +Needs, +Capacities, +K): the jobs using resource K stay within its capacity
resource_limit(Starts, Durations, Ends, Needs, Capacities, K) :-
    nth0(K, Capacities, Capacity),
    job_tasks(Starts, Durations, Ends, Needs, K, Tasks),
    cumulative(Tasks, [limit(Capacity)]).

% job_tasks(+Starts, +Durations, +Ends, +Needs, +K, -Tasks): one task per job, using the need of resource K
job_tasks([], [], [], [], _, []).
% a job of zero duration uses no time on any resource, so it is left out (cumulative/2 rejects such tasks)
job_tasks([_|Ss], [0|Ds], [_|Es], [_|Ns], K, Ts) :-
    !,
    job_tasks(Ss, Ds, Es, Ns, K, Ts).
job_tasks([S|Ss], [D|Ds], [E|Es], [N|Ns], K, [task(S, D, E, Need, _)|Ts]) :-
    nth0(K, N, Need),
    job_tasks(Ss, Ds, Es, Ns, K, Ts).

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
