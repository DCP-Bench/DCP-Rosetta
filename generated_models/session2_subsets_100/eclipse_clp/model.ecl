% session2_subsets_100: an ECLiPSe model from DCP Rosetta.
%
% From a set A of different integers, find two disjoint non-empty subsets S and T whose elements have equal
% sums. S and T need not together cover all of A. Give S and T as one 0/1 flag per element of A, 1 when the
% element is in the subset.
%
% Save this file as model.ecl. Download `session2_subsets_100.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session2_subsets_100.json
%   eclipse -b model.ecl -e "run('session2_subsets_100_1.dat'), halt"

% A: the set of integers, indexed from 0 as in the JSON.

:- lib(ic).
:- lib(lists).

% In_S and In_T: one 0/1 flag per element of A, 1 when the element is in that subset.
model(Instance, Vars, [in_S-InS, in_T-InT]) :-
    memberchk('A'-As, Instance),
    length(As, N),
    length(InS, N),
    length(InT, N),
    InS :: 0..1,
    InT :: 0..1,
    % S and T are disjoint: no element is in both
    ( foreach(S, InS), foreach(T, InT) do S + T #=< 1 ),
    % S and T are both non-empty
    sum(InS) #>= 1,
    sum(InT) #>= 1,
    % the elements of S and the elements of T have equal sums
    As * InS #= As * InT,
    append(InS, InT, Vars).

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
