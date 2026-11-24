% hidato: an ECLiPSe model from DCP Rosetta.
%
% A Hidato puzzle is a grid partly filled with numbers, the other cells being empty. Fill in the
% empty cells so that the grid holds each number from 1 to the number of cells exactly once, and
% consecutive numbers touch horizontally, vertically or diagonally.
%
% Save this file as model.ecl. Download `hidato.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py hidato.json
%   eclipse -b model.ecl -e "run('hidato_1.dat'), halt"

:- lib(gfd).
:- lib(listut).

% The data field puzzle is the grid as a list of rows, with 0 for each empty cell.
model(Data, Vars, [x-Rows]) :-
    memberchk(puzzle-Puzzle, Data),
    length(Puzzle, NRows),
    Puzzle = [FirstRow | _],
    length(FirstRow, NCols),
    N is NRows * NCols,                    % the number of cells, which is the largest number
    % the grid, with every cell a number from 1 to N
    length(Rows, NRows),
    ( foreach(Row, Rows), param(NCols, N) do
        length(Row, NCols),
        ( foreach(X, Row), param(N) do X :: 1..N )
    ),
    flatten(Rows, Flat),
    % the numbers already in the puzzle stay where they are
    flatten(Puzzle, Givens),
    ( foreach(X, Flat), foreach(G, Givens) do
        ( G =:= 0 -> true ; X = G )
    ),
    % each number from 1 to N is in the grid exactly once
    alldifferent(Flat),
    % Ls[K] is the position of the number K in the grid, counted from 1 along the rows
    length(Ls, N),
    ( foreach(L, Ls), param(N) do L :: 1..N ),
    ( for(K, 1, N), foreach(L, Ls), param(Flat) do
        element(L, Flat, K)
    ),
    % the row and column of each position: position L is row R, column C
    length(Rs, N),
    length(Cs, N),
    ( foreach(L, Ls), foreach(R, Rs), foreach(C, Cs), param(NRows, NCols) do
        R :: 1..NRows,
        C :: 1..NCols,
        L #= (R - 1) * NCols + C
    ),
    % each number touches the next one horizontally, vertically or diagonally
    adjacent(Rs, Cs),
    append(Ls, Rs, LsRs),
    append(LsRs, Cs, LsRsCs),
    append(LsRsCs, Flat, Vars).

% consecutive positions differ by at most one row and at most one column
adjacent([_], [_]).
adjacent([R1, R2 | Rs], [C1, C2 | Cs]) :-
    R1 - R2 #=< 1,
    R2 - R1 #=< 1,
    C1 - C2 #=< 1,
    C2 - C1 #=< 1,
    adjacent([R2 | Rs], [C2 | Cs]).

:- lib(branch_and_bound).

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
