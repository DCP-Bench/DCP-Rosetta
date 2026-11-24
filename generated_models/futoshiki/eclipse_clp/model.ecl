% futoshiki: an ECLiPSe model from DCP Rosetta.
%
% The futoshiki puzzle is played on a square grid, such as 5 x 5. The objective is to place the numbers 1 to 5 (or
% whatever the dimensions are) such that each row and each column contains each of the digits 1 to 5. Some digits may be
% given at the start. In addition, inequality constraints are also initially specified between some of the squares, such
% that one must be higher or lower than its neighbour. These constraints must be honoured as the grid is filled out.
%
% Save this file as model.ecl. Download `futoshiki.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py futoshiki.json
%   eclipse -b model.ecl -e "run('futoshiki_1.dat'), halt"
%
% The data fields: values is the grid of given digits, one list per row, with 0 for an empty cell; lt lists the
% inequalities as [R1, C1, R2, C2] (1-based), meaning that the cell in row R1, column C1 is less than the cell in row R2,
% column C2.

:- lib(ic).
:- lib(listut).

% Grid is the N x N grid of cells, as a list of rows.
model(Instance, Vars, [grid-Grid], none) :-
    memberchk(values-Values, Instance),
    memberchk(lt-Lt, Instance),
    length(Values, N),
    grid_rows(N, N, Grid),
    flatten(Grid, Vars),

    % the given digits keep their value
    givens(Values, Grid),

    % each row contains each of the digits 1 to N once
    all_rows_different(Grid),

    % each column contains each of the digits 1 to N once
    all_columns_different(Grid, 1, N),

    % each inequality is honoured: the first cell is smaller than the second
    inequalities(Lt, Grid).

% grid_rows(+R, +N, -Rows): R rows of N cells, each cell a digit from 1 to N
grid_rows(0, _, []) :- !.
grid_rows(R, N, [Row|Rows]) :-
    length(Row, N),
    Row :: 1..N,
    R1 is R - 1,
    grid_rows(R1, N, Rows).

% givens(+ValRows, ?GridRows): a given digit (not 0) fixes its cell
givens([], []).
givens([ValRow|ValRows], [GridRow|GridRows]) :-
    givens_row(ValRow, GridRow),
    givens(ValRows, GridRows).

givens_row([], []).
givens_row([V|Vs], [X|Xs]) :-
    ( V =:= 0 -> true ; X #= V ),
    givens_row(Vs, Xs).

all_rows_different([]).
all_rows_different([Row|Rows]) :-
    alldifferent(Row),
    all_rows_different(Rows).

all_columns_different(_, J, N) :- J > N, !.
all_columns_different(Grid, J, N) :-
    column(Grid, J, Col),
    alldifferent(Col),
    J1 is J + 1,
    all_columns_different(Grid, J1, N).

% column(+Grid, +J, -Col): the cells of column J
column([], _, []).
column([GridRow|GridRows], J, [X|Xs]) :-
    nth1(J, GridRow, X),
    column(GridRows, J, Xs).

inequalities([], _).
inequalities([[R1, C1, R2, C2]|Ineqs], Grid) :-
    nth1(R1, Grid, Row1), nth1(C1, Row1, A),
    nth1(R2, Grid, Row2), nth1(C2, Row2, B),
    A #< B,
    inequalities(Ineqs, Grid).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

:- lib(branch_and_bound).

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
