% three_coins: a SWI-Prolog model from DCP Rosetta.
%
% Three coins lie on a table in the order tails, heads, tails. In precisely three moves make them face either all
% heads or all tails. Each move consists of choosing one coin and flipping it over.
%
% Save this file as model.pl. Download `three_coins.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('three_coins.json')" -t halt model.pl
%
% Data fields: init (the starting face of each coin, 1 for tails and 0 for heads, lists indexed from 0) and num_moves
% (the number of moves).
:- use_module(library(clpfd)).

model(Instance, [Later, Flags], [steps-Steps]) :-
    Init = Instance.init,
    NumMoves = Instance.num_moves,
    length(Init, Coins),
    length(Later, NumMoves),               % the configuration after each move
    Steps = [Init|Later],
    maplist(coin_row(Coins), Later),
    % each move flips exactly one coin
    moves(Steps, Flags),
    % the final configuration has all coins facing the same way
    last(Steps, Final),
    Final = [F|Rest],
    maplist(#=(F), Rest).

coin_row(Coins, Row) :-
    length(Row, Coins),
    Row ins 0..1.                          % 1 is tails, 0 is heads

moves([_], []).
moves([Before, After|Rest], [Flags|MoreFlags]) :-
    one_flip(Before, After, Flags),
    moves([After|Rest], MoreFlags).

% Exactly one coin differs between the two configurations: Flags[C] = 1 when coin C is the one flipped.
one_flip(Before, After, Flags) :-
    maplist(flip_or_keep, Before, After, Flags),
    sum(Flags, #=, 1).

flip_or_keep(Before, After, Flag) :-
    Flag in 0..1,
    (Flag #= 1) #==> (After #= 1 - Before),
    (Flag #= 0) #==> (After #= Before).

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
