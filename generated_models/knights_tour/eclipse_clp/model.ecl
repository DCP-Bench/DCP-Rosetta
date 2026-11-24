% knights_tour: an ECLiPSe model from DCP Rosetta.
%
% A knight's tour is a sequence of moves of a knight on a chessboard such that the knight visits every square exactly
% once, without returning to the starting square. Find a knight's tour on an N x N chessboard, where each square holds
% the number of the move on which the knight visits it, numbered from 0 to N*N-1.
%
% Save this file as model.ecl. Download `knights_tour.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py knights_tour.json
%   eclipse -b model.ecl -e "run('knights_tour_1.dat'), halt"
%
% The data fields: n is the size N of the chessboard (N x N squares).

:- lib(ic).

% Output x: the chessboard as N rows of N move numbers, x[R][C] is the move number of the square in row R, column C.
%
% The squares are numbered 1 to NN = N*N row by row, and an extra node Dummy = NN+1 closes the tour: the successor
% of Dummy is the first square of the tour, and the successor of the last square is Dummy. So one circuit through all
% the nodes is a path through all the squares that does not have to return to its start.
model(Instance, Vars, [x-Rows]) :-
    memberchk(n-N, Instance),
    NN is N * N,
    Dummy is NN + 1,

    % Succ[I] is the square visited after square I; Succ[Dummy] is the first square visited
    length(Squares, NN),
    set_move_domains(Squares, 1, N, Dummy),
    DummySucc :: 1..NN,
    app(Squares, [DummySucc], Succ),

    % the successors form one circuit through all the squares and the dummy node
    circuit(Succ),

    % the move number of each square: 0 for the first square, 0 to NN-1 in all, all different
    length(Moves, NN),
    Moves :: 0..NN-1,
    alldifferent(Moves),
    app(Moves, [-1], MovesExt),          % the dummy node has no move number, -1
    element(DummySucc, MovesExt, 0),     % the first square of the tour is move 0

    % each square is followed by the square of the next move, or by the dummy node after the last move
    successor_moves(Squares, Moves, MovesExt),

    % the chessboard: row R holds the move numbers of the squares in that row
    split_rows(Moves, N, Rows),

    app(Succ, Moves, Vars).

% the successor of each square is a square a knight's move away, or the dummy node
set_move_domains([], _, _, _).
set_move_domains([S | Ss], I, N, Dummy) :-
    knight_targets(I, N, Targets),
    S :: [Dummy | Targets],
    I1 is I + 1,
    set_move_domains(Ss, I1, N, Dummy).

% the squares a knight's move away from square I (numbered from 1) on an N x N board
knight_targets(I, N, Targets) :-
    R is (I - 1) // N,
    C is (I - 1) mod N,
    knight_offsets(Offsets),
    targets(Offsets, R, C, N, Targets).

knight_offsets([[1, 2], [2, 1], [2, -1], [1, -2], [-1, 2], [-2, 1], [-2, -1], [-1, -2]]).

% the squares at the given offsets from row R, column C, that are on the board
targets([], _, _, _, []).
targets([[DR, DC] | Offsets], R, C, N, Targets) :-
    R2 is R + DR,
    C2 is C + DC,
    (   R2 >= 0, R2 < N, C2 >= 0, C2 < N
    ->  Targets = [T | Rest],
        T is R2 * N + C2 + 1
    ;   Targets = Rest
    ),
    targets(Offsets, R, C, N, Rest).

% a square's move number is followed by the move number of its successor, unless the successor is the dummy node
% (the last move), where the successor's move number is -1
successor_moves([], [], _).
successor_moves([S | Ss], [M | Ms], MovesExt) :-
    element(S, MovesExt, V),
    NextIsMove #= (V #= M + 1),
    NextIsDummy #= (V #= -1),
    NextIsMove + NextIsDummy #>= 1,
    successor_moves(Ss, Ms, MovesExt).

% the list split into rows of N items each
split_rows([], _, []).
split_rows(Items, N, [Row | Rows]) :-
    take(N, Items, Row, Rest),
    split_rows(Rest, N, Rows).

take(0, Rest, [], Rest) :- !.
take(K, [X | Xs], [X | Ys], Rest) :-
    K1 is K - 1,
    take(K1, Xs, Ys, Rest).

app([], Ys, Ys).
app([X | Xs], Ys, [X | Zs]) :-
    app(Xs, Ys, Zs).

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
