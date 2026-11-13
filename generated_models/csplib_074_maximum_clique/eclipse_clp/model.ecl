% csplib_074_maximum_clique: an ECLiPSe model from DCP Rosetta.
%
% Given a simple undirected graph, a clique is a set of vertices every two distinct vertices of which are adjacent.
% Find a clique of the largest possible size.
%
% Save this file as model.ecl. Download `csplib_074_maximum_clique.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_074_maximum_clique.json
%   eclipse -b model.ecl -e "run('csplib_074_maximum_clique_1.dat'), halt"
%
% The data fields: n is the number of vertices, adj the adjacency matrix (adj[I][J] is 1 when vertices I and J are
% adjacent), indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Cs[I] is 1 when vertex I is in the clique, 0 otherwise.
model(Instance, Cs, [c-Cs], max(sum(Cs))) :-
    memberchk(n-N, Instance),
    memberchk(adj-Adj, Instance),
    length(Cs, N),
    Cs :: 0..1,

    % every two distinct vertices of the clique are adjacent, so two vertices that are not adjacent cannot both be in it
    ( for(I, 0, N-2), param(Adj, Cs, N) do
        ( for(J, I+1, N-1), param(Adj, Cs, I) do
            nth0(I, Adj, RowI), nth0(J, RowI, A1),
            nth0(J, Adj, RowJ), nth0(I, RowJ, A2),
            ( A1 =:= 1, A2 =:= 1 -> true
            ; nth0(I, Cs, CI), nth0(J, Cs, CJ), CI + CJ #=< 1
            )
        )
    ).

search_goal(Cs) :-
    search(Cs, 0, first_fail, indomain_max, complete, []).
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
