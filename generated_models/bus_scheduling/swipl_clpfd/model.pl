% bus_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% A city plans a mass-transit bus system. The demand for buses is taken as constant over successive 4-hour intervals of
% the day, which is cyclic: the first interval follows the last. Each bus works 8 successive hours, so a bus that starts
% in one interval also works in the next. In each interval, the buses available there (those starting in it and those
% that started in the interval before) must meet the demand for that interval. Find the minimum number of buses needed.
%
% Save this file as model.pl. Download `bus_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('bus_scheduling.json')" -t halt model.pl
%
% Data fields: demands (the number of buses needed in each 4-hour interval, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, [Total|X], [x-X], min(Total)) :-
    Demands = Instance.demands,
    length(Demands, Slots),
    length(X, Slots),                       % X[I]: the number of buses starting in interval I, counted from 0
    sum_list(Demands, Largest),
    X ins 0..Largest,
    Last is Slots - 1,
    numlist(0, Last, Intervals),
    maplist(covered(X, Demands, Slots), Intervals),
    sum(X, #=, Total).                      % the buses in all, to be made as few as possible

% The interval I has enough buses: those starting in it and those that started in the interval before (cyclically).
covered(X, Demands, Slots, I) :-
    Previous is (I + Slots - 1) mod Slots,
    nth0(I, X, Starting),
    nth0(Previous, X, Started),
    nth0(I, Demands, Demand),
    Starting + Started #>= Demand.

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
