% bananas: an ECLiPSe model from DCP Rosetta.
%
% Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes cost seven dollars, and three apples
% cost nine dollars. Purchase 100 fruits for 100 dollars. All types of fruits need to be purchased, but the number of
% bananas and apples together should be as small as possible.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% Output: the quantity of each fruit bought.
model(_Instance, [B, O, M, A], [bananas-B, oranges-O, mangoes-M, apples-A], min(B + A)) :-
    % every type of fruit is bought, at least one of each
    [B, O, M, A] #:: 1..100,
    % 100 fruits are bought in total
    B + O + M + A #= 100,
    % the 100 fruits cost 100 dollars: the prices are scaled by 315 to keep them integral
    % (a banana costs 3/5 dollar, an orange 5/7, a mango 7/9, an apple 3 dollars; 315 * 100 = 31500)
    189 * B + 225 * O + 245 * M + 945 * A #= 31500.
    % the objective is the number of bananas and apples together, to be as small as possible

:- lib(branch_and_bound).

% Builds the model, solves it and prints each output.
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
