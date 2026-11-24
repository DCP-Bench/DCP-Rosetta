% crypta: a SWI-Prolog model from DCP Rosetta.
%
% Cryptarithmetic puzzle: each letter stands for a different digit from 0 to 9, and the first letter of each number
% is not zero. The addition is
%
%     B A I J J A J I I A H F C F E B B J E A
%   + D H F G A B C D I D B I F F A G F E J E
%   = G J E G A C D D H F A F J B F I H E E F
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl

:- use_module(library(clpfd)).

model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I, 'J'-J]) :-
    Letters = [A, B, C, D, E, F, G, H, I, J],
    % each letter is a different digit
    Letters ins 0..9,
    all_distinct(Letters),
    % the first letter of each of the three numbers is not zero
    B #>= 1,
    D #>= 1,
    G #>= 1,
    % the numbers, written with their digits from the least significant column
    X = [B, A, I, J, J, A, J, I, I, A, H, F, C, F, E, B, B, J, E, A],
    Y = [D, H, F, G, A, B, C, D, I, D, B, I, F, F, A, G, F, E, J, E],
    Z = [G, J, E, G, A, C, D, D, H, F, A, F, J, B, F, I, H, E, E, F],
    reverse(X, Xr),
    reverse(Y, Yr),
    reverse(Z, Zr),
    % column by column, the digits of X and Y plus the carry from the column before give the digit of Z and a carry
    % into the next column; there is no carry into the first column nor out of the last one
    add_columns(Xr, Yr, Zr, 0, 0, Carries),
    append(Letters, Carries, Vars).

add_columns([], [], [], Carry, Carry, []).
add_columns([Xd|Xs], [Yd|Ys], [Zd|Zs], CarryIn, CarryOut, [CarryNext|Carries]) :-
    CarryNext in 0..1,
    Xd + Yd + CarryIn #= Zd + 10 * CarryNext,
    add_columns(Xs, Ys, Zs, CarryNext, CarryOut, Carries).

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
