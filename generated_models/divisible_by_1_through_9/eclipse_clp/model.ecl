% divisible_by_1_through_9: an ECLiPSe model from DCP Rosetta.
%
% Find a 10 digit number that uses each of the digits 0 to 9 exactly once, and where the number formed by the first
% n digits is divisible by n, for every n from 1 to 10. Read the digits from left to right: the number a is
% divisible by 1, the number ab by 2, the number abc by 3, and so on up to the whole number.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data.

:- lib(ic).
:- lib(lists).

model(_Instance, Vars, [digits-Digits]) :-
    length(Digits, 10),
    Digits :: 0..9,
    % each of the digits 0 to 9 is used exactly once
    alldifferent(Digits),
    % a 10 digit number does not start with zero
    Digits = [First, D2, _, D4, D5, D6, _, D8, _, D10],
    First #\= 0,
    % a prefix is divisible by n only when its last digit allows it: an even last digit for 2, 4, 6 and 8,
    % 0 or 5 for 5, and 0 for 10
    D2 :: [0, 2, 4, 6, 8],
    D4 :: [0, 2, 4, 6, 8],
    D6 :: [0, 2, 4, 6, 8],
    D8 :: [0, 2, 4, 6, 8],
    D5 :: [0, 5],
    D10 #= 0,
    % for each n from 1 to 10, the number formed by the first n digits is divisible by n:
    % the number is n times a quotient Q, which is at most the largest n digit number divided by n
    (   for(N, 1, 10), foreach(Q, Quotients), param(Digits) do
        length(Prefix, N),
        append(Prefix, _, Digits),
        % the value of the prefix, digit by digit from the left
        (   foreach(D, Prefix), fromto(0, A, B, Value) do
            B #= 10 * A + D
        ),
        Largest is (10 ^ N - 1) // N,
        Q :: 0..Largest,
        Value #= N * Q
    ),
    append(Digits, Quotients, Vars).

% the digits are chosen from the left, so each prefix is checked as soon as it is complete
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run :-
    solve_model([]).

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
