% csplib_044_steiner: an ECLiPSe model from DCP Rosetta.
%
% The ternary Steiner problem of order n consists of finding a set of n(n-1)/6 triples of distinct integer elements in
% {1, ..., n} such that any two triples have at most one common element.
%
% Save this file as model.ecl. Download `csplib_044_steiner.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_044_steiner.json
%   eclipse -b model.ecl -e "run('csplib_044_steiner_1.dat'), halt"
%
% The instance field: n (the order of the Steiner system).

:- lib(ic).
:- lib(branch_and_bound).

% Output sets: Rows[T][E] is 1 when element E (counting from 1) is part of triple T.
model(Instance, Vars, [sets-Rows]) :-
    memberchk(n-N, Instance),
    T is N * (N - 1) // 6,                 % the number of triples
    length(Rows, T),
    ( foreach(Row, Rows), param(N) do length(Row, N) ),
    flatten(Rows, Vars),
    Vars :: 0..1,

    % each triple has three distinct elements
    ( foreach(Row, Rows) do sum(Row) #= 3 ),

    % any two triples have at most one common element
    ( fromto(Rows, [RowA|Later], Later, []) do
        ( foreach(RowB, Later), param(RowA) do
            ( foreach(XA, RowA), foreach(XB, RowB), foreach(P, Ps) do P #= XA * XB ),
            sum(Ps) #=< 1
        )
    ).

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
