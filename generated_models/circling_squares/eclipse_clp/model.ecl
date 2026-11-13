% circling_squares: an ECLiPSe model from DCP Rosetta.
%
% Circling the squares: place a different whole number in each of the ten squares arranged in a circle, so that the sum
% of the squares of any two adjacent numbers equals the sum of the squares of the two numbers diametrically opposite to
% them. Fractions are not allowed, and no number needs more than two figures. The numbers placed are A = 16, B = 2,
% F = 8 and G = 14; fill in the other six.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"
%
% This problem has no data fields: the given numbers above are part of the model.
%
% The squares run around the circle in the order A, B, C, D, E, F, G, H, I, K, so the two squares diametrically opposite
% a pair of neighbours are the pair five places further on.
:- lib(ic).
:- lib(branch_and_bound).

model(_Instance, [A, B, C, D, E, F, G, H, I, K], ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I, 'K'-K]) :-
    % each number is a positive whole number of at most two figures
    [A, B, C, D, E, F, G, H, I, K] :: 1..99,
    % the ten numbers are all different
    alldifferent([A, B, C, D, E, F, G, H, I, K]),
    % the given numbers
    A #= 16, B #= 2, F #= 8, G #= 14,
    % the squares of A and B equal the squares of the opposite pair F and G
    A * A + B * B #= F * F + G * G,
    % the squares of B and C equal the squares of the opposite pair G and H
    B * B + C * C #= G * G + H * H,
    % the squares of C and D equal the squares of the opposite pair H and I
    C * C + D * D #= H * H + I * I,
    % the squares of D and E equal the squares of the opposite pair I and K
    D * D + E * E #= I * I + K * K,
    % the squares of E and F equal the squares of the opposite pair K and A
    E * E + F * F #= K * K + A * A.

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
