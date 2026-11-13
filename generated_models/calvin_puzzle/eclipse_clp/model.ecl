% calvin_puzzle: an ECLiPSe model from DCP Rosetta.
%
% Fill an n by n grid with the numbers 1 to n^2, each used once, so that each number follows the previous one by a move of
% one of two types, starting from any square. If the next number is placed vertically or horizontally, it is placed exactly
% three squares away from the previous number. If the next number is placed diagonally, it is placed exactly two squares
% away from the previous number. Find the completed grid, as a list of rows of integers.
%
% Save this file as model.ecl. Download `calvin_puzzle.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py calvin_puzzle.json
%   eclipse -b model.ecl -e "run('calvin_puzzle_1.dat'), halt"

% Fields read: n is the size of the grid (n by n squares).

:- lib(ic).
:- lib(lists).
:- lib(listut).

% whether the move from square C1 to square C2 (both numbered row by row from 1) is one of the two allowed types
move_value(C1, C2, N, V) :-
    R1 is (C1 - 1) // N, Co1 is (C1 - 1) mod N,
    R2 is (C2 - 1) // N, Co2 is (C2 - 1) mod N,
    DR is R2 - R1, DC is Co2 - Co1,
    (   ( DR =:= 0, abs(DC) =:= 3 ; abs(DR) =:= 3, DC =:= 0 ; abs(DR) =:= 2, abs(DC) =:= 2 )
    ->  V = 1
    ;   V = 0
    ).

% Output x: the completed grid, row by row, each row a list of the numbers in its squares.
model(Instance, Cells, [x-Grid]) :-
    memberchk(n-N, Instance),
    NN is N * N,
    % the square in which each number K is placed, numbered row by row from 1
    length(Cells, NN),
    Cells :: 1..NN,
    alldifferent(Cells),
    % table of the allowed moves: entry (C1-1)*NN + C2 is 1 when the move from square C1 to square C2 is allowed
    ( for(C1, 1, NN), foreach(Row, TableRows), param(N, NN) do
        ( for(C2, 1, NN), foreach(V, Row), param(C1, N) do
            move_value(C1, C2, N, V)
        )
    ),
    flatten(TableRows, Table),
    % consecutive numbers K and K+1 are in squares joined by an allowed move
    ( for(K, 1, NN-1), param(Cells, Table, NN) do
        K1 is K + 1,
        nth1(K, Cells, C1), nth1(K1, Cells, C2),
        Index #= (C1 - 1) * NN + C2,
        element(Index, Table, 1)
    ),
    % the grid: the number in each square, the inverse of the sequence of squares
    length(Gs, NN),
    Gs :: 1..NN,
    ( for(K, 1, NN), param(Cells, Gs) do
        nth1(K, Cells, CK),
        element(CK, Gs, K)
    ),
    ( for(R, 1, N), foreach(Row, Grid), param(Gs, N) do
        ( for(C, 1, N), foreach(V, Row), param(Gs, N, R) do
            Idx is (R - 1) * N + C,
            nth1(Idx, Gs, V)
        )
    ).

search_goal(Cells) :-
    search(Cells, 0, first_fail, indomain_min, complete, []).

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
