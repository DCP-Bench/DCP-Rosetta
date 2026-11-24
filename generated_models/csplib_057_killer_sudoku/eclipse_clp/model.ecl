% csplib_057_killer_sudoku: an ECLiPSe model from DCP Rosetta.
%
% Killer sudoku: fill the grid with the numbers 1 to 9 so that every row, every column and every 3x3 nonet contains
% each number exactly once, the numbers in each cage sum to the small number printed in its corner, and no number
% appears more than once in a cage.
%
% Save this file as model.ecl. Download `csplib_057_killer_sudoku.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_057_killer_sudoku.json
%   eclipse -b model.ecl -e "run('csplib_057_killer_sudoku_1.dat'), halt"
%
% The data fields: n is the side of the grid (9), problem lists the cages, each as [Sum, Cells] where Cells lists the
% [Row, Column] cells of the cage, 1-based.

:- lib(ic).
:- lib(listut).

% Grid[R][C] is the number in row R and column C, both 1-based.
model(Instance, Vars, [x-Grid], none) :-
    memberchk(n-N, Instance),
    memberchk(problem-Cages, Instance),
    length(Grid, N),
    ( foreach(Row, Grid), param(N) do
        length(Row, N),
        Row :: 1..N
    ),
    flatten(Grid, Vars),

    % each row contains each number exactly once
    ( foreach(Row, Grid) do
        alldifferent(Row)
    ),

    % each column contains each number exactly once
    ( for(C, 1, N), param(Grid) do
        column(Grid, C, Col),
        alldifferent(Col)
    ),

    % each 3x3 nonet contains each number exactly once
    ( for(BR, 0, 2), param(Grid) do
        ( for(BC, 0, 2), param(Grid, BR) do
            nonet_cells(Grid, BR, BC, Cells),
            alldifferent(Cells)
        )
    ),

    % each cage: its numbers sum to the number in its corner, and no number repeats in the cage
    ( foreach([Sum, Coords], Cages), param(Grid) do
        cells_of(Grid, Coords, CageVars),
        sum(CageVars) #= Sum,
        alldifferent(CageVars)
    ).

% the cells of column C, top to bottom
column(Grid, C, Col) :-
    ( foreach(Row, Grid), foreach(X, Col), param(C) do
        nth1(C, Row, X)
    ).

% the nine cells of the 3x3 nonet in block row BR and block column BC (both 0-based)
nonet_cells(Grid, BR, BC, Cells) :-
    R0 is 3 * BR, C0 is 3 * BC,
    ( for(DR, 1, 3), foreach(Cs, Rows), param(Grid, R0, C0) do
        ( for(DC, 1, 3), foreach(X, Cs), param(Grid, R0, C0, DR) do
            R is R0 + DR, C is C0 + DC,
            nth1(R, Grid, Row), nth1(C, Row, X)
        )
    ),
    flatten(Rows, Cells).

% the cells at the given 1-based [Row, Column] coordinates, in order
cells_of(Grid, Coords, Vars) :-
    ( foreach([R, C], Coords), foreach(V, Vars), param(Grid) do
        nth1(R, Grid, Row),
        nth1(C, Row, V)
    ).

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
