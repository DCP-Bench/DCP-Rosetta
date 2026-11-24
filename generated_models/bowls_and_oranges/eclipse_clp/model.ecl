% bowls_and_oranges: an ECLiPSe model from DCP Rosetta.
%
% There are bowls numbered from 1 and placed in a line at exact intervals of 1 meter, and a number of oranges. All the
% oranges are placed in the bowls, no more than one orange in each bowl, so that there are no three oranges A, B and C
% such that the distance between A and B equals the distance between B and C. Find the bowls in which the oranges are
% placed, in ascending order.
%
% Save this file as model.ecl. Download `bowls_and_oranges.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py bowls_and_oranges.json
%   eclipse -b model.ecl -e "run('bowls_and_oranges_1.dat'), halt"

% Fields read: n is the number of bowls, m is the number of oranges.

:- lib(ic).
:- lib(lists).
:- lib(listut).

% Output x: the bowl of each orange, in ascending order.
model(Instance, Xs, [x-Xs]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    length(Xs, M),
    Xs :: 1..N,
    % no more than one orange in each bowl: the oranges are in strictly ascending bowls
    ( for(I, 1, M-1), param(Xs) do
        nth1(I, Xs, XI),
        I1 is I + 1,
        nth1(I1, Xs, XNext),
        XI #< XNext
    ),
    % no three oranges in bowls I < J < K are equally spaced: the middle bowl is not the mean of the other two
    ( for(I, 1, M), param(Xs, M) do
        ( for(J, I+1, M), param(Xs, I, M) do
            ( for(K, J+1, M), param(Xs, I, J) do
                nth1(I, Xs, XI), nth1(J, Xs, XJ), nth1(K, Xs, XK),
                2 * XJ #\= XI + XK
            )
        )
    ).

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
