% football: an ECLiPSe model from DCP Rosetta.
%
% Statistics show that, in the Premiership, there is a strong correlation between the value of a team's players and
% their final position in that league, so you want to spend as much money as you can. The chairman gives you an upper
% limit of GBP 30 million, so you want your purchases to add up to as close to that figure as possible (without going
% over). Goalkeepers (must buy 1 exactly): g1 0.73, g2 1.28, g3 3.88. Defenders (must buy 2 or more): d1 0.92, d2 1.31,
% d3 1.62, d4 2.41, d5 2.79, d6 3.28, d7 3.91, d8 4.57. Midfielders (must buy 3 or more): m1 1.8, m2 2.63, m3 3.17,
% m4 3.769, m5 4.14, m6 4.75, m7 5.38, m8 5.93, m9 6.78, m10 7.13. Strikers (must buy 2 or more): s1 4.46, s2 6.47,
% s3 7.78, s4 8.39, s5 9.5. Prices are in GBP millions. Also, you must buy at least eleven players in total.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% Each player is a 0/1 variable: 1 when the player is bought. Prices are in GBP thousands, so all sums are whole numbers.
model(_Instance, Vars, [z-Z], max(Z)) :-
    Goalkeeper = [730, 1280, 3880],
    Defender   = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
    Midfielder = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
    Striker    = [4460, 6470, 7780, 8390, 9500],
    length(Goalkeeper, NG), length(Defender, ND),
    length(Midfielder, NM), length(Striker, NS),
    length(Gs, NG), length(Ds, ND), length(Ms, NM), length(Ss, NS),
    Gs :: 0..1, Ds :: 0..1, Ms :: 0..1, Ss :: 0..1,
    append(Gs, Ds, GD), append(GD, Ms, GDM), append(GDM, Ss, Vars),

    % exactly one goalkeeper is bought
    sum(Gs) #= 1,

    % at least two defenders are bought
    sum(Ds) #>= 2,

    % at least three midfielders are bought
    sum(Ms) #>= 3,

    % at least two strikers are bought
    sum(Ss) #>= 2,

    % at least eleven players are bought in total
    sum(Vars) #>= 11,

    % z is the total price of the players bought
    weighted_terms(Goalkeeper, Gs, GT),
    weighted_terms(Defender, Ds, DT),
    weighted_terms(Midfielder, Ms, MT),
    weighted_terms(Striker, Ss, ST),
    append(GT, DT, GTD), append(GTD, MT, GTDM), append(GTDM, ST, Terms),
    sum(Terms) #= Z,

    % the total price does not go over GBP 30 million (30000 thousands)
    Z #=< 30000.

% weighted_terms(+Prices, +Selections, -Terms): the list of price * selection terms.
weighted_terms([], [], []).
weighted_terms([P|Ps], [X|Xs], [P*X|Ts]) :-
    weighted_terms(Ps, Xs, Ts).

% Builds the model, solves it and prints each output.
run :- solve_model([]).

:- lib(branch_and_bound).

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
