% csplib_003_quasigroup_existence: an ECLiPSe model from DCP Rosetta.
%
% Quasigroup existence, problem QG3: an order m quasigroup is an m by m multiplication table in
% which each element occurs once in every row and every column (a Latin square). Find an order m
% quasigroup with the QG3 property, (a*b)*(b*a) = a for all elements a and b.
%
%
% Save this file as model.ecl. Download `csplib_003_quasigroup_existence.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_003_quasigroup_existence.json
%   eclipse -b model.ecl -e "run('csplib_003_quasigroup_existence_1.dat'), halt"

% Field read from the data: m (the order of the quasigroup, the number of elements).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['quasigroup'-Out]) :-
    memberchk(m-M, Instance),
    % the table has m rows of m entries; the entries are the elements 1 to m here
    % (element/3 counts from 1), and the output numbers them from 0
    length(Rows, M),
    ( foreach(RowT, Rows), param(M) do
        length(RowT, M),
        RowT :: 1..M,
        % each element occurs once in every row
        alldifferent(RowT)
    ),
    % each element occurs once in every column
    ( for(ColN, 1, M), param(Rows) do
        ( foreach(RowC, Rows), foreach(Entry, ColumnC), param(ColN) do
            nth1(ColN, RowC, Entry)
        ),
        alldifferent(ColumnC)
    ),
    flatten(Rows, Flat),
    % (a*b)*(b*a) = a for all elements a and b: the table entry at row a*b and column b*a is a
    ( for(A, 1, M), param(Rows, Flat, M) do
        ( for(B, 1, M), param(Rows, Flat, M, A) do
            nth1(A, Rows, RowA), nth1(B, RowA, AB),
            nth1(B, Rows, RowB), nth1(A, RowB, BA),
            Index #= (AB - 1) * M + BA,
            element(Index, Flat, A)
        )
    ),
    % the output: the table with its elements numbered from 0
    ( foreach(RowO, Rows), foreach(OutRow, Out) do
        ( foreach(Cell, RowO), foreach(Shifted, OutRow) do
            Shifted #= Cell - 1
        )
    ),
    Vars = Flat.

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
