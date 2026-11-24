% heterosquare: an ECLiPSe model from DCP Rosetta.
%
% A heterosquare of order n is an n by n square whose elements are distinct integers from 1 to n*n,
% such that the sums of its rows, columns and two diagonals are all different from one another.
%
% Save this file as model.ecl. Download `heterosquare.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py heterosquare.json
%   eclipse -b model.ecl -e "run('heterosquare_1.dat'), halt"

:- lib(gfd).
:- lib(listut).

% The data field n is the order of the square: n rows and n columns.
model(Data, Vars, [x-Rows]) :-
    memberchk(n-N, Data),
    Max is N * N,
    % Rows[I][J] is the element in row I and column J
    length(Rows, N),
    ( foreach(Row, Rows), param(N, Max) do
        length(Row, N),
        ( foreach(V, Row), param(Max) do V :: 1..Max )
    ),
    flatten(Rows, Cells),
    % the elements are distinct integers from 1 to n*n
    alldifferent(Cells),
    % the sums of the rows
    ( for(I, 1, N), foreach(S, RowSums), param(Rows) do
        nth1(I, Rows, Row),
        sum(Row) #= S
    ),
    % the sums of the columns
    ( for(J, 1, N), foreach(S, ColSums), param(Rows) do
        column(Rows, J, Col),
        sum(Col) #= S
    ),
    % the sums of the two diagonals: the main one, and the one from the top right corner
    ( for(I, 1, N), foreach(V, Diag), param(Rows) do
        nth1(I, Rows, Row),
        nth1(I, Row, V)
    ),
    ( for(I, 1, N), foreach(V, Anti), param(Rows, N) do
        nth1(I, Rows, Row),
        K is N + 1 - I,
        nth1(K, Row, V)
    ),
    sum(Diag) #= D1,
    sum(Anti) #= D2,
    % the sums of the rows, columns and diagonals are all different
    append(RowSums, ColSums, RowColSums),
    append(RowColSums, [D1, D2], Sums),
    alldifferent(Sums),
    append(Cells, Sums, Vars).

% column(Rows, J, Col): Col holds the elements of column J
column(Rows, J, Col) :-
    ( foreach(Row, Rows), foreach(V, Col), param(J) do
        nth1(J, Row, V)
    ).

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
