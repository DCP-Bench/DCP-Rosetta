% csplib_076_costas_arrays: an ECLiPSe model from DCP Rosetta.
%
% A Costas array is a pattern of n marks on an n x n grid, one mark per row and one per column, in which the
% n(n-1)/2 vectors between the marks are all different. Equivalently, the difference triangle built from the
% permutation X_1..X_n, with the differences X_i - X_(i+l) on each line l, has no value repeated within a line.
%
% Save this file as model.ecl. Download `csplib_076_costas_arrays.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_076_costas_arrays.json
%   eclipse -b model.ecl -e "run('csplib_076_costas_arrays_1.dat'), halt"
%
% The data field n is the size of the grid, which is also the number of marks.

:- lib(ic).
:- lib(listut).

% Xs[I] is the column (1-based) of the mark in row I (1-based).
model(Instance, Xs, [costas-Xs]) :-
    memberchk(n-N, Instance),
    length(Xs, N),
    Xs :: 1..N,

    % one mark per column
    alldifferent(Xs),

    % the difference triangle: on each line L the differences X_I - X_(I+L) are all different
    ( for(L, 1, N-1), param(Xs, N) do
        M is N - L,
        ( for(I, 1, M), foreach(D, Diffs), param(Xs, L) do
            J is I + L,
            nth1(I, Xs, XI), nth1(J, Xs, XJ),
            D #= XI - XJ
        ),
        alldifferent(Diffs)
    ).

search_goal(Xs) :-
    search(Xs, 0, first_fail, indomain_min, complete, []).
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
