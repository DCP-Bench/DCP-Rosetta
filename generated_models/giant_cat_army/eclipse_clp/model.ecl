% giant_cat_army: an ECLiPSe model from DCP Rosetta.
%
% Start with the list [0] and build it by one of three operations on its last number: add 5, add 7,
% or take the square root (when that is an integer). The finished list has 24 numbers, all distinct,
% all integers at most 60, starts with 0 and ends with 14, and contains 2, 10 and 14 in that order,
% with other numbers allowed between them.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(gfd).
:- lib(listut).

% The model reads no data fields: the list is built from the rules above.
model(_Instance, Vars, [x-X]) :-
    Len = 24,                              % the list has 24 numbers
    length(X, Len),
    X :: 0..60,                            % every number is an integer at most 60
    % the list starts with 0
    nth1(1, X, 0),
    % and ends with 14
    nth1(Len, X, 14),
    % all the numbers are distinct
    alldifferent(X),
    % each number after the first comes from the one before it by adding 5, adding 7 or taking the square root
    step_rules(X),
    % 2, 10 and 14 appear on the list in that order: the positions of 2 and 10 are
    % ordered, 10 comes before the final 14, and both are labelled with the list
    Vars = [P2, P10 | X],
    P2 :: 1..Len,
    P10 :: 1..Len,
    element(P2, X, 2),
    element(P10, X, 10),
    P2 #< P10,
    P10 #< Len.

% each pair of neighbouring numbers follows one of the three operations
step_rules([_]).
step_rules([A, B | Rest]) :-
    (   (B #= A + 5) or (B #= A + 7) or (A #= B * B)
    ),
    step_rules([B | Rest]).

:- lib(branch_and_bound).

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
