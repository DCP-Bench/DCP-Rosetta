% hanging_weights: an ECLiPSe model from DCP Rosetta.
%
% Weights A to M hang from a system of bars. The weights have different integer values from 1 to 13,
% and must be such that every bar balances about its pivot: the weights on either side of a pivot,
% each multiplied by its distance from the pivot, are equal, and a bar hanging beneath another
% contributes its total weight as though it were a single weight.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(gfd).
:- lib(listut).

% The model reads no data fields: the weights are the unknowns of the puzzle.
model(_Instance, Vars, [a-A, b-B, c-C, d-D, e-E, f-F, g-G, h-H, i-I, j-J, k-K, l-L, m-M]) :-
    Vars = [A, B, C, D, E, F, G, H, I, J, K, L, M],
    % the weights have different values from 1 to 13
    Vars :: 1..13,
    alldifferent(Vars),
    % the bottom right bar: 5*C = D
    5 * C #= D,
    % the bar above it: 3*G = 2*(C+D)
    3 * G #= 2 * (C + D),
    % the bottom left bar: 4*A = B
    4 * A #= B,
    % the bar holding J and K: the bar of A and B hangs three units to the left of the pivot, J two units
    % to the left, K one unit to the right, and the bar of G, C and D hangs two units to the right
    3 * (A + B) + 2 * J #= K + 2 * (G + C + D),
    % the bar holding E and F: 3*E = 2*F
    3 * E #= 2 * F,
    % the bar holding H and I: H three units to the left, the bar E+F two units and I three units to the right
    3 * H #= 2 * (E + F) + 3 * I,
    % the bar holding L and M: the bar H+I+E+F one unit to the left, L one unit and M four units to the right
    (H + I + E + F) #= L + 4 * M,
    % the top bar: the bar L+M+H+I+E+F four units to the left of its pivot balances the bar of the
    % other weights three units to the right
    4 * (L + M + H + I + E + F) #= 3 * (J + K + A + B + G + C + D).

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
