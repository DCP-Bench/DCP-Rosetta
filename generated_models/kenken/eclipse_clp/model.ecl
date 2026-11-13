% kenken: an ECLiPSe model from DCP Rosetta.
%
% Fill an N x N grid with the digits 1 to N so that each row and each column contains each digit exactly once, and
% each cage (a group of cells, given with a target number but no operation) achieves its target with one of the
% operations addition, subtraction, multiplication or division. A cage of one cell holds its target. A cage of two
% cells may use any of the four operations, and a division must be exact. A larger cage uses either addition or
% multiplication. Digits may repeat within a cage.
%
% Save this file as model.ecl. Download `kenken.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py kenken.json
%   eclipse -b model.ecl -e "run('kenken_1.dat'), halt"
%
% The data fields: n is the size N of the grid; problem is the list of cages, each one a list [Target, Cells] where
% Target is the target number of the cage and Cells lists its cells as [Row, Column], 1-based.

:- lib(ic).

% Output x: the grid as N rows of N digits.
model(Instance, Vars, [x-Rows]) :-
    memberchk(n-N, Instance),
    memberchk(problem-Cages, Instance),
    length(Rows, N),
    ( foreach(Row, Rows), param(N) do length(Row, N) ),
    flatten_rows(Rows, Vars),

    % each cell holds a digit from 1 to N
    Vars :: 1..N,

    % each row contains each digit exactly once
    ( foreach(Row, Rows) do alldifferent(Row) ),

    % each column contains each digit exactly once
    columns_of(Rows, Columns),
    ( foreach(Col, Columns) do alldifferent(Col) ),

    % each cage achieves its target number with one of the four operations
    ( foreach([Target, Cells], Cages), param(Rows) do
        cage_values(Cells, Rows, Values),
        cage(Values, Target)
    ).

% the search picks the cell with the fewest candidate digits first and tries the lowest digit first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% a cage of one cell holds its target
cage([V], Target) :-
    V #= Target.

% a cage of two cells: sum, difference, product or exact quotient equals the target
cage([A, B], Target) :-
    (   (A + B #= Target)
    or  (A - B #= Target)
    or  (B - A #= Target)
    or  (A * B #= Target)
    or  (A #= Target * B)
    or  (B #= Target * A)
    ).

% a larger cage: the sum or the product of its digits equals the target
cage(Values, Target) :-
    Values = [_, _, _ | _],
    cell_product(Values, P),
    (   (sum(Values) #= Target)
    or  (P #= Target)
    ).

% the product of a list of digits
cell_product([V], V).
cell_product([V, W | Ws], V * P) :-
    cell_product([W | Ws], P).

% the digits in the cells of a cage, in the order of its cells
cage_values([], _, []).
cage_values([[R, C] | Cells], Rows, [V | Vs]) :-
    grid_cell(Rows, R, C, V),
    cage_values(Cells, Rows, Vs).

grid_cell(Rows, R, C, V) :-
    nth_item(R, Rows, Row),
    nth_item(C, Row, V).

% the I-th item of a list, counting from 1
nth_item(1, [X | _], X) :- !.
nth_item(I, [_ | Xs], X) :-
    I > 1,
    I1 is I - 1,
    nth_item(I1, Xs, X).

% the cells of the grid as one list, row after row
flatten_rows([], []).
flatten_rows([Row | Rows], Vars) :-
    app(Row, Rest, Vars),
    flatten_rows(Rows, Rest).

app([], Ys, Ys).
app([X | Xs], Ys, [X | Zs]) :-
    app(Xs, Ys, Zs).

% the columns of the grid: the first column is the list of the first cells of all rows, and so on
columns_of([[] | _], []) :- !.
columns_of(Rows, [Col | Cols]) :-
    heads_tails(Rows, Col, Tails),
    columns_of(Tails, Cols).

heads_tails([], [], []).
heads_tails([[H | T] | Rows], [H | Hs], [T | Ts]) :-
    heads_tails(Rows, Hs, Ts).

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
