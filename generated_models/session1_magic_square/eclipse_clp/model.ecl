% session1_magic_square: an ECLiPSe model from DCP Rosetta.
%
% A magic square is an n x n grid (n != 2) such that each cell contains a different integer from 1 to n^2 and the sum of
% the integers in each row, column and diagonal is equal. Find a magic square for a given size n, knowing that the sum
% of integers of each row, column and diagonal has to be equal to n(n^2 + 1)/2 (integer).
%
% Save this file as model.ecl. Download `session1_magic_square.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session1_magic_square.json
%   eclipse -b model.ecl -e "run('session1_magic_square_1.dat'), halt"
%
% The data field: n is the size of the square, which has n rows and n columns.

:- lib(ic).
:- lib(listut).
:- lib(lists).

% Output square: the n rows of the magic square, each a list of n integers.
model(Instance, Cells, [square-Rows]) :-
    memberchk(n-N, Instance),
    NSquared is N*N,
    Total is N*(N*N + 1) // 2,
    length(Rows, N),
    ( foreach(Row, Rows), param(N) do
        length(Row, N)
    ),
    append(Rows, Cells),
    Cells :: 1..NSquared,

    % each cell contains a different integer
    alldifferent(Cells),

    % the sum of the integers in each row is the magic sum
    ( foreach(Row, Rows), param(Total) do
        sum(Row) #= Total
    ),

    % the sum of the integers in each column is the magic sum
    ( for(C, 1, N), param(Rows, Total) do
        ( foreach(Row, Rows), param(C), foreach(X, Column) do
            nth1(C, Row, X)
        ),
        sum(Column) #= Total
    ),

    % the sum of the integers on the main diagonal is the magic sum
    ( for(I, 1, N), param(Rows), foreach(X, MainDiagonal) do
        nth1(I, Rows, Row),
        nth1(I, Row, X)
    ),
    sum(MainDiagonal) #= Total,

    % the sum of the integers on the other diagonal is the magic sum
    ( for(I, 1, N), param(Rows, N), foreach(X, OtherDiagonal) do
        nth1(I, Rows, Row),
        J is N + 1 - I,
        nth1(J, Row, X)
    ),
    sum(OtherDiagonal) #= Total.

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
