% ages_of_the_sons: an ECLiPSe model from DCP Rosetta.
%
% An old man asked a mathematician to guess the ages of his three sons. The product of their ages is 36. The
% mathematician needs more information. The sum of their ages equals the number of windows in a building he can
% see; the mathematician still needs more information. The oldest son has blue eyes, and then the mathematician
% knows the ages. What are the ages of the three sons, starting from the oldest?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% This problem has no instance data: the model reads nothing from the instance.
:- lib(ic).

model(_Instance, [A1, A2, A3], ['A1'-A1, 'A2'-A2, 'A3'-A3]) :-
    % the sums of the ages that more than one set of three ages can give, with product 36
    ambiguous_sums(Sums),
    % the ages are whole numbers, at least 1, and listed from the oldest
    [A1, A2, A3] #:: 1..36,
    A1 #>= A2, A2 #>= A3,
    % the product of their ages is 36
    A1 * A2 * A3 #= 36,
    % the sum of their ages is one of the ambiguous sums, so the mathematician still needs more information
    Total #= A1 + A2 + A3,
    Total #:: Sums,
    % the oldest son is older than the other two, so there is one oldest son
    A1 #> A2.

% All sets of three ages (oldest first) with product 36, and then the sums that more than one set gives.
ambiguous_sums(Sums) :-
    findall(S, (age_between(1, 36, A), age_between(1, A, B), age_between(1, B, C),
                A * B * C =:= 36, S is A + B + C), AllSums),
    sort(AllSums, Distinct),
    findall(S, (age_member(S, Distinct), findall(S, age_member(S, AllSums), Same), Same = [_, _ | _]), Sums).

% X ranges over the integers Low..High
age_between(Low, High, Low) :- Low =< High.
age_between(Low, High, X) :- Low < High, Low1 is Low + 1, age_between(Low1, High, X).

age_member(X, [X | _]).
age_member(X, [_ | Xs]) :- age_member(X, Xs).

:- lib(branch_and_bound).

% Reads nothing, builds the model, solves it and prints each output.
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
