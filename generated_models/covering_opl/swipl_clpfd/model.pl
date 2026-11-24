% covering_opl: a SWI-Prolog model from DCP Rosetta.
%
% Select a set of workers to perform all the tasks, while minimizing the cost. Each worker can perform certain tasks
% and has a hiring cost. Ensure that all tasks are performed.
%
% Save this file as model.pl. Download `covering_opl.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('covering_opl.json')" -t halt model.pl
%
% Data fields: nb_workers (the number of workers), num_tasks (the number of tasks), Cost (the hiring cost of each
% worker, lists indexed from 0), Qualified (for each task, the 1-based numbers of the workers who can perform it).
:- use_module(library(clpfd)).

model(Instance, Vars, [total_cost-TotalCost, workers-Workers], min(TotalCost)) :-
    NbWorkers = Instance.nb_workers,
    NumTasks = Instance.num_tasks,
    get_dict('Cost', Instance, Cost),
    get_dict('Qualified', Instance, Qualified),
    length(Workers, NbWorkers),
    Workers ins 0..1,                      % Workers[W] is 1 when worker W+1 is hired
    sum_list(Cost, CostSum),
    TotalCost in 0..CostSum,
    % the total cost is the hiring cost of the workers hired
    scalar_product(Cost, Workers, #=, TotalCost),
    length(Qualified, NumTasks),
    % every task is performed by a hired worker who can perform it
    maplist(task_covered(Workers), Qualified),
    Vars = [TotalCost|Workers].

% at least one of the qualified workers of the task is hired
task_covered(Workers, WorkerIds) :-
    maplist(hired(Workers), WorkerIds, Hired),
    sum(Hired, #>=, 1).

hired(Workers, WorkerId, H) :-
    nth1(WorkerId, Workers, H).

:- use_module(library(http/json)).

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
