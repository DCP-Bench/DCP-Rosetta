% knights_tour: a SWI-Prolog model from DCP Rosetta.
%
% A knight's tour is a sequence of moves of a knight on a chessboard such that the knight visits every square
% exactly once (without returning to the starting square). Find a knight's tour on an n by n chessboard, and give
% each square the number of the move on which it is visited, the numbers running from 0 to n*n-1.
%
% Save this file as model.pl. Download `knights_tour.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('knights_tour.json')" -t halt model.pl
%
% Data fields: n (the size of the chessboard, n by n).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Path-Numbers, [x-Rows]) :-
    N = Instance.n,
    Squares is N * N,
    Last is Squares - 1,
    % Path[T] is the square visited on move T; squares are numbered row * N + column, from 0
    length(Path, Squares),
    Path ins 0..Last,
    % the knight visits every square exactly once
    all_distinct(Path),
    % each move goes from a square to a square one knight's move away
    knight_moves(N, Moves),
    chain_moves(Path, Moves),
    % Rows[I][J] is the move number of square (I, J); the rows are flattened into Numbers
    length(Rows, N),
    maplist({N}/[Row]>>length(Row, N), Rows),
    append(Rows, Numbers),
    Numbers ins 0..Last,
    % the square visited on move T is numbered T
    numlist(0, Last, Ts),
    maplist(numbered_on_move(Numbers), Path, Ts).

% knight_moves(+N, -Moves): the pairs [From, To] of squares one knight's move apart on an N by N board, where a move
% goes two squares along one direction and one along the other
knight_moves(N, Moves) :-
    Max is N - 1,
    findall([From, To],
            (   between(0, Max, I), between(0, Max, J), From is I * N + J,
                member([DI, DJ], [[1, 2], [2, 1], [-1, 2], [-2, 1], [1, -2], [2, -1], [-1, -2], [-2, -1]]),
                I2 is I + DI, J2 is J + DJ,
                between(0, Max, I2), between(0, Max, J2),
                To is I2 * N + J2
            ),
            Moves).

% each square is followed by a square one knight's move away
chain_moves([From, To|Rest], Moves) :-
    !,
    tuples_in([[From, To]], Moves),
    chain_moves([To|Rest], Moves).
chain_moves(_, _).

% the square Square is numbered Move in the flattened board
numbered_on_move(Numbers, Square, Move) :-
    Index #= Square + 1,
    element(Index, Numbers, Move).

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
