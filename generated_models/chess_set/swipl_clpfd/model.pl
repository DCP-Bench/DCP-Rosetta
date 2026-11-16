% chess_set: a SWI-Prolog model from DCP Rosetta.
%
% A small joinery makes two sizes of boxwood chess sets. The small set needs 3 hours of machining on a lathe and
% 1 kg of boxwood, and the large set needs 2 hours on a lathe and 3 kg of boxwood. There are four lathes, each
% worked 40 hours a week, and only 200 kg of boxwood a week can be obtained. A large set yields a profit of $20 and a
% small set a profit of $5. Decide how many sets of each kind to make each week so as to maximise the profit.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Vars, [small_set-Small, large_set-Large, max_profit-Profit], max(Profit)) :-
    [Small, Large] ins 0..200,             % numbers of small and large sets made in a week
    % the boxwood used is no more than the 200 kg available: 1 kg per small set, 3 kg per large set
    Small + 3 * Large #=< 200,
    % the lathe hours used are no more than 4 lathes x 40 hours = 160: 3 per small set, 2 per large set
    3 * Small + 2 * Large #=< 160,
    % the profit: $5 per small set and $20 per large set, to be maximised
    Profit #= 5 * Small + 20 * Large,
    Profit in 0..10000,
    Vars = [Small, Large, Profit].

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
