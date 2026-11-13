% discrete_tomography: an ECLiPSe model from DCP Rosetta.
%
% A matrix of zeroes and ones is x-rayed vertically and horizontally, giving the number of ones in each row and
% in each column. Reconstruct the matrix from these counts.
%
% Save this file as model.ecl. Download `discrete_tomography.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py discrete_tomography.json
%   eclipse -b model.ecl -e "run('discrete_tomography_1.dat'), halt"

% Data fields: row_sums (the number of ones in each row, a list indexed from 0), col_sums (the number of ones
% in each column, a list indexed from 0). The matrix output matrix has one row per row sum and one column per
% column sum.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, [matrix-Rows]) :-
    memberchk(row_sums-RowSums, Instance),
    memberchk(col_sums-ColSums, Instance),
    length(RowSums, R),
    length(ColSums, C),
    % the matrix has R rows and C columns, each cell a zero or a one
    length(Rows, R),
    (   foreach(Row, Rows), param(C) do
        length(Row, C),
        Row :: 0..1
    ),
    % each row has as many ones as its count
    (   foreach(Row, Rows), foreach(S, RowSums) do
        sum(Row) #= S
    ),
    % each column has as many ones as its count
    (   for(J, 1, C), foreach(S, ColSums), param(Rows) do
        (   foreach(Row, Rows), foreach(X, Col), param(J) do
            nth1(J, Row, X)
        ),
        sum(Col) #= S
    ),
    % the variables are all the cells, row by row
    append(Rows, Vars).

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
