% five_brigands: a SWI-Prolog model from DCP Rosetta.
%
% The five Spanish brigands Alfonso, Benito, Carlos, Diego and Esteban counted their spoils after a raid and found
% that together they had exactly 200 doubloons. If Alfonso had twelve times as much, Benito three times as much,
% Carlos the same amount, Diego half as much and Esteban one-third as much, they would still have altogether 200
% doubloons. How many doubloons could each have had, with no brigand having less than one doubloon?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% No data fields: the model reads nothing from the data.
:- use_module(library(clpfd)).

model(_Instance, [A, B, C, D, E], ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E]) :-
    % each brigand has at least one doubloon
    [A, B, C, D, E] ins 1..200,
    % together they have exactly 200 doubloons
    A + B + C + D + E #= 200,
    % with 12A, 3B, C, D/2 and E/3 they still have 200; multiplied by 6 to keep the coefficients whole
    72*A + 18*B + 6*C + 3*D + 2*E #= 1200.

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
