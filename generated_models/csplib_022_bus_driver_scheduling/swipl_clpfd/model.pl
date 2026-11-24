% csplib_022_bus_driver_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% Bus driver scheduling: given a set of tasks (pieces of work) to cover and a large set of possible shifts, where each
% shift covers a subset of the tasks, select a subset of shifts that covers each piece of work exactly once. The goal is
% to cover all tasks while minimising the total number of shifts used; every shift has the same cost.
%
% Save this file as model.pl. Download `csplib_022_bus_driver_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_022_bus_driver_scheduling.json')" -t halt model.pl
%
% Data fields: num_work (the number of tasks, numbered from 0), num_shifts (the number of shifts) and shifts (the tasks
% each shift covers, one list per shift, tasks numbered from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-X], min(Total)) :-
    NumWork = Instance.num_work,
    NumShifts = Instance.num_shifts,
    Shifts = Instance.shifts,
    Last is NumWork - 1,
    % X[S] is 1 when shift S is selected, 0 otherwise
    length(X, NumShifts),
    X ins 0..1,
    % the number of shifts selected, to minimise
    Total in 0..NumShifts,
    sum(X, #=, Total),
    Vars = [Total|X],
    % each task is covered by exactly one selected shift
    numlist(0, Last, Tasks),
    maplist(covered_once(Shifts, X), Tasks).

% the selected shifts that cover task W: exactly one of them
covered_once(Shifts, X, W) :-
    maplist(covers(W), Shifts, Coefficients),
    scalar_product(Coefficients, X, #=, 1).

% Coefficient is 1 when the shift covers task W, 0 otherwise
covers(W, Shift, C) :-
    (   memberchk(W, Shift) -> C = 1 ; C = 0 ).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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
