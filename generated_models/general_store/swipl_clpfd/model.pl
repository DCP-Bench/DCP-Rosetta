% general_store: a SWI-Prolog model from DCP Rosetta.
%
% The owner of a general store has put up a sign: the words above the line are numbers that add up to ALL WOOL.
% Each different letter stands for a different digit. The sixteen words CHESS, CASH, BOWWOW, CHOPS, ALSOPS, PALEALE,
% COOL, BASS, HOPS, ALES, HOES, APPLES, COWS, CHEESE, CHSOAP and SHEEP, each read as a number, add up to ALLWOOL.
% Leading zeros are allowed: a word may start with the digit 0. Give the digit of each letter A, B, C, E, H, L, O,
% P, S and W.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% No data fields: the model reads nothing from the data.
:- use_module(library(clpfd)).

model(_Instance, [A, B, C, E, H, L, O, P, S, W], ['A'-A, 'B'-B, 'C'-C, 'E'-E, 'H'-H, 'L'-L, 'O'-O, 'P'-P, 'S'-S, 'W'-W]) :-
    % each letter stands for a different digit
    [A, B, C, E, H, L, O, P, S, W] ins 0..9,
    all_different([A, B, C, E, H, L, O, P, S, W]),
    % the words above the line, each read as a number
    maplist(word_value, [[C,H,E,S,S], [C,A,S,H], [B,O,W,W,O,W], [C,H,O,P,S], [A,L,S,O,P,S],
                         [P,A,L,E,A,L,E], [C,O,O,L], [B,A,S,S], [H,O,P,S], [A,L,E,S], [H,O,E,S],
                         [A,P,P,L,E,S], [C,O,W,S], [C,H,E,E,S,E], [C,H,S,O,A,P], [S,H,E,E,P]], Values),
    % their total is ALL WOOL
    word_value([A,L,L,W,O,O,L], AllWool),
    sum(Values, #=, AllWool).

% the number written by a list of digits, most significant first
word_value(Digits, Value) :-
    foldl(digit_step, Digits, 0, Value).

digit_step(Digit, Acc0, Acc) :-
    Acc #= Acc0*10 + Digit.

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
