% csplib_050_diamond_free: an ECLiPSe model from DCP Rosetta.
%
% Find a simple undirected graph on N vertices (no loops, at most one edge between two vertices) that is diamond-free:
% no set of four vertices has five or more edges between them. Every vertex has a degree that is greater than zero and
% divisible by 3, and the sum of the degrees is divisible by 12.
%
% Save this file as model.ecl. Download `csplib_050_diamond_free.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_050_diamond_free.json
%   eclipse -b model.ecl -e "run('csplib_050_diamond_free_1.dat'), halt"
%
% The instance field: N (the number of vertices).

:- lib(ic).
:- lib(branch_and_bound).
:- lib(listut).

% Output matrix: Rows[I][J] is 1 when vertices I and J (counting from 1) are adjacent.
model(Instance, Vars, [matrix-Rows]) :-
    memberchk('N'-N, Instance),
    length(Rows, N),
    ( foreach(Row, Rows), param(N) do length(Row, N) ),

    % the adjacency matrix: no loops, and symmetric; the edge {I, J} is a 0/1 variable
    ( for(I, 1, N), param(Rows, N) do
        ( for(J, 1, N), param(Rows, I) do
            nth1(I, Rows, RowI),
            nth1(J, RowI, X),
            (   I =:= J -> X = 0
            ;   I < J -> X :: 0..1, nth1(J, Rows, RowJ), nth1(I, RowJ, X)
            ;   true
            )
        )
    ),
    flatten(Rows, Cells),
    Vars = Cells,

    % each vertex has a degree that is greater than zero and divisible by 3
    ( foreach(Row, Rows), foreach(D, Degrees), foreach(Q, Quotients), param(N) do
        sum(Row) #= D,
        D #= 3 * Q,
        Q :: 1..N
    ),

    % the sum of the degrees is divisible by 12
    sum(Degrees) #= 12 * K,
    K :: 0..N * N,

    % diamond-free: any four vertices have at most four edges between them
    ( for(A, 1, N), param(Rows, N) do
        ( for(B, 1, N), param(Rows, A, N) do
            ( for(C, 1, N), param(Rows, A, B, N) do
                ( for(D, 1, N), param(Rows, A, B, C) do
                    (   A < B, B < C, C < D
                    ->  cell(Rows, A, B, E1), cell(Rows, A, C, E2), cell(Rows, A, D, E3),
                        cell(Rows, B, C, E4), cell(Rows, B, D, E5), cell(Rows, C, D, E6),
                        sum([E1, E2, E3, E4, E5, E6]) #=< 4
                    ;   true
                    )
                )
            )
        )
    ).

% the entry of the matrix in row I and column J
cell(Rows, I, J, X) :-
    nth1(I, Rows, Row),
    nth1(J, Row, X).

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
