% csplib_028_bibd: an ECLiPSe model from DCP Rosetta.
%
% A balanced incomplete block design (BIBD) arranges v distinct objects into b blocks such that each block contains
% exactly k distinct objects, each object occurs in exactly r different blocks, and every two distinct objects occur
% together in exactly lambda blocks. Equivalently, its v by b incidence matrix is a binary matrix with exactly r ones per
% row, k ones per column, and a scalar product of lambda between any pair of distinct rows.
%
% Save this file as model.ecl. Download `csplib_028_bibd.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_028_bibd.json
%   eclipse -b model.ecl -e "run('csplib_028_bibd_1.dat'), halt"
%
% The instance fields: v (objects), b (blocks), r (blocks per object), k (objects per block), l (lambda, blocks shared by
% each pair of objects).

:- lib(ic).
:- lib(branch_and_bound).

% Output matrix: Rows[I][J] is 1 when object I is in block J, counting from 1.
model(Instance, Vars, [matrix-Rows]) :-
    memberchk(v-V, Instance),
    memberchk(b-B, Instance),
    memberchk(r-R, Instance),
    memberchk(k-K, Instance),
    memberchk(l-L, Instance),
    length(Rows, V),                       % one row per object
    ( foreach(Row, Rows), param(B) do length(Row, B) ),
    flatten(Rows, Vars),
    Vars :: 0..1,

    % each object occurs in exactly r blocks
    ( foreach(Row, Rows), param(R) do sum(Row) #= R ),

    % each block contains exactly k objects
    ( for(J, 1, B), param(Rows, K) do
        ( foreach(Row, Rows), foreach(X, Col), param(J) do element(J, Row, X) ),
        sum(Col) #= K
    ),

    % every two distinct objects occur together in exactly lambda blocks: the scalar product of their rows is lambda
    ( fromto(Rows, [RowA|Later], Later, []) do
        ( foreach(RowB, Later), param(RowA, L) do
            ( foreach(XA, RowA), foreach(XB, RowB), foreach(P, Ps) do P #= XA * XB ),
            sum(Ps) #= L
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
