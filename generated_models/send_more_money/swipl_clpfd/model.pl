% send_more_money: a SWI-Prolog model from DCP Rosetta.
%
% The SEND + MORE = MONEY puzzle: assign a digit to each letter so that the sum
%
%    SEND
%  + MORE
%  ------
%   MONEY
%
% holds. Each letter stands for a unique digit from 0 to 9, and the first letter of each word is not zero.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Vars holds the digit of each letter: S, E, N, D, M, O, R, Y.
model(_Instance, Vars, [s-S, e-E, n-N, d-D, m-M, o-O, r-R, y-Y]) :-
    Vars = [S, E, N, D, M, O, R, Y],
    % each letter is a digit from 0 to 9
    Vars ins 0..9,
    % each letter stands for a different digit
    all_distinct(Vars),
    % SEND + MORE = MONEY
    1000 * S + 100 * E + 10 * N + D
    + 1000 * M + 100 * O + 10 * R + E
    #= 10000 * M + 1000 * O + 100 * N + 10 * E + Y,
    % the first letter of each word is not zero
    S #> 0,
    M #> 0.

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
