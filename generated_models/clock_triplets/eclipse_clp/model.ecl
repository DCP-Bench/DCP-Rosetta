% clock_triplets: an ECLiPSe model from DCP Rosetta.
%
% Rearrange the numbers 1 to 12 on the face of a clock so that no triplet of adjacent numbers has a sum higher than 21.
% The triplets wrap around the clock, so the last two numbers and the first form a triplet too, and so on.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"
%
% This problem has no data fields: the clock size and the limit of 21 are part of the model.
:- lib(ic).
:- lib(listut).
:- lib(branch_and_bound).

% Outputs: x (the twelve numbers on the clock, in order around the face).
model(_Instance, Xs, [x-Xs]) :-
    % the clock has twelve positions
    N = 12,
    length(Xs, N),
    % the numbers placed are 1 to 12, each used once
    Xs :: 1..N,
    alldifferent(Xs),
    % the triplets wrap around, so repeat the first two numbers at the end of the ring
    Xs = [First, Second | _],
    append(Xs, [First, Second], Ring),
    % no triplet of adjacent numbers sums to more than 21
    no_big_triplet(Ring).

% no_big_triplet(Ring): every three consecutive numbers of Ring sum to at most 21
no_big_triplet([A, B, C | Rest]) :-
    A + B + C #=< 21,
    no_big_triplet([B, C | Rest]).
no_big_triplet([_, _]).

run :- solve_model([]).

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
