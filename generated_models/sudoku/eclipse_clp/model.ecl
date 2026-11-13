% sudoku: an ECLiPSe model from DCP Rosetta.
%
% Sudoku: fill a 9x9 grid with numbers so that each row, each column and each of the nine 3x3 sections contains
% every digit from 1 to 9 exactly once. Some cells are already filled in, and they keep their digits; the other
% cells are empty.
%
% Save this file as model.ecl. Download `sudoku.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py sudoku.json
%   eclipse -b model.ecl -e "run('sudoku_1.dat'), halt"

% input_grid: the nine rows of the given grid, indexed from 0 as in the JSON; 0 marks an empty cell and a digit a filled cell.

:- lib(ic).
:- lib(lists).
:- lib(listut).

% Grid: the digits of the solved grid, one list per row.
model(Instance, Vars, [grid-Rows]) :-
    memberchk(input_grid-Input, Instance),
    length(Input, 9),
    % every cell holds a digit from 1 to 9, and a digit already given stays in its cell
    ( foreach(InRow, Input), foreach(Cells1, Rows) do
        length(Cells1, 9),
        Cells1 :: 1..9,
        ( foreach(Given, InRow), foreach(V1, Cells1) do
            ( Given =:= 0 -> true ; V1 #= Given )
        )
    ),
    append(Rows, Vars),
    % each row contains every digit once
    ( foreach(Row2, Rows) do
        alldifferent(Row2)
    ),
    % each column contains every digit once
    ( for(C, 1, 9), param(Rows) do
        ( foreach(Row3, Rows), foreach(X3, Column), param(C) do
            nth1(C, Row3, X3)
        ),
        alldifferent(Column)
    ),
    % each of the nine 3x3 sections contains every digit once
    ( for(B, 0, 8), param(Rows) do
        R0 is (B // 3) * 3,
        C0 is (B mod 3) * 3,
        box_cells(Rows, R0, C0, Cells),
        alldifferent(Cells)
    ).

% Cells: the nine cells of the 3x3 section that starts after row R0 and column C0 (both counted from 0)
box_cells(Rows, R0, C0, Cells) :-
    ( for(DR, 1, 3), foreach(Segment, Segments), param(Rows, R0, C0) do
        R is R0 + DR,
        nth1(R, Rows, Row),
        ( for(DC, 1, 3), foreach(X, Segment), param(Row, C0) do
            C is C0 + DC,
            nth1(C, Row, X)
        )
    ),
    append(Segments, Cells).

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
