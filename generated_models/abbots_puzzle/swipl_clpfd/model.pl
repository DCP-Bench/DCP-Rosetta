% abbots_puzzle: a SWI-Prolog model from DCP Rosetta.
%
% If 100 bushels of corn were distributed among 100 people such that each man received three bushels, each woman
% two, and each child half a bushel, and there are five times as many women as men, find the number of men, women,
% and children.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields.
:- use_module(library(clpfd)).

model(_Instance, [Men, Women, Children], [children-Children, men-Men, women-Women]) :-
    People = 100,
    Bushels = 100,
    [Men, Women, Children] ins 0..People,
    % the 100 people are men, women and children
    Men + Women + Children #= People,
    % there are five times as many women as men
    Women #= 5 * Men,
    % the 100 bushels: 3 for each man, 2 for each woman, 1/2 for each child (doubled to stay in integers)
    6 * Men + 4 * Women + Children #= 2 * Bushels.

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
