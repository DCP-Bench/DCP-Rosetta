% coins_grid: an ECLiPSe model from DCP Rosetta.
%
% On an n by n grid, place coins so that: in each row exactly c coins are placed; in each column exactly c coins are
% placed; each cell holds at most one coin; and the sum, over all coins, of the squared horizontal distance from the main
% diagonal is as small as possible. For a coin in row i and column j this distance is (i - j)^2.
%
% Save this file as model.ecl. Download `coins_grid.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py coins_grid.json
%   eclipse -b model.ecl -e "run('coins_grid_1.dat'), halt"
%
% Data fields: n is the side of the grid and c the number of coins in each row and in each column.
:- lib(ic).
:- lib(listut).
:- lib(branch_and_bound).

% Outputs: x (whether a coin is placed in each cell, row by row) and z (the total squared distance from the diagonal).
model(Instance, Vars, [x-Rows, z-Z], min(Z)) :-
    memberchk(n-N, Instance),
    memberchk(c-C, Instance),
    length(Rows, N),
    bool_rows(Rows, N),
    % in each row exactly c coins are placed
    rows_sum_to(Rows, C),
    % in each column exactly c coins are placed
    columns_of(Rows, Cols),
    rows_sum_to(Cols, C),
    % the squared distance of each cell from the main diagonal, in the same row-by-row order as the cells
    distances(1, N, Weights),
    sum(Weights) #= Ub,
    % the total squared distance of the coins from the main diagonal is to be minimized
    flatten(Rows, Flat),
    Z :: 0..Ub,
    Z #= Weights * Flat,
    append(Flat, [Z], Vars).

% bool_rows(Rows, N): Rows is a list of N rows, each of N 0/1 variables
bool_rows([], _).
bool_rows([Row | Rows], N) :-
    length(Row, N),
    Row :: 0..1,
    bool_rows(Rows, N).

% rows_sum_to(Rows, C): each row of Rows sums to C
rows_sum_to([], _).
rows_sum_to([Row | Rows], C) :-
    sum(Row) #= C,
    rows_sum_to(Rows, C).

% distances(I, N, Ws): the squared distances (I - J)^2 for every row I from I to N and column J, row by row
distances(I, N, []) :-
    I > N, !.
distances(I, N, Ws) :-
    row_distances(I, 1, N, Row),
    I1 is I + 1,
    distances(I1, N, Rest),
    append(Row, Rest, Ws).

row_distances(_, J, N, []) :-
    J > N, !.
row_distances(I, J, N, [W | Ws]) :-
    W is (I - J) * (I - J),
    J1 is J + 1,
    row_distances(I, J1, N, Ws).

% columns_of(Rows, Cols): Cols is the transpose of the matrix Rows
columns_of([[] | _], []) :- !.
columns_of(Rows, [Col | Cols]) :-
    firsts_rests(Rows, Col, Rest),
    columns_of(Rest, Cols).

firsts_rests([], [], []).
firsts_rests([[H | T] | Rs], [H | Hs], [T | Ts]) :-
    firsts_rests(Rs, Hs, Ts).

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
