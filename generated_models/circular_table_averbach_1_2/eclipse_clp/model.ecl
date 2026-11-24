% circular_table_averbach_1_2: an ECLiPSe model from DCP Rosetta.
%
% Three players, X, Y and Z, of different nationalities (American, English, French) sit around a circular table playing
% a game of Hearts. Each passes three cards to the person on their right. Y passed three hearts to the American. X
% passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman. Determine the
% nationality of each person.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"
%
% This problem has no data fields: the clues above are part of the model. Seats are numbered 0, 1, 2 around the table,
% with seat 1 to the right of seat 0, seat 2 to the right of seat 1, and seat 0 to the right of seat 2.
:- lib(ic).
:- lib(branch_and_bound).

% Outputs: x, y and z (the seat of each player X, Y and Z), and american, english and french (the seat of the player of
% each nationality), so that equal values denote the same person.
model(_Instance, [X, Y, Z, American, English, French, Passer],
      [x-X, y-Y, z-Z, american-American, english-English, french-French]) :-
    % the three players sit in three different seats
    [X, Y, Z] :: 0..2,
    alldifferent([X, Y, Z]),
    % the nationalities belong to three different players
    [American, English, French] :: 0..2,
    alldifferent([American, English, French]),
    % the seat to the right of seat p is seat (p + 1) mod 3
    % Y passed hearts to the American, so the American sits on Y's right
    Y1 #= Y + 1,
    element(Y1, [1, 2, 0], American),
    % X passed to the person on X's right (Passer), who passed to the Frenchwoman, so the Frenchwoman sits on Passer's right
    X1 #= X + 1,
    element(X1, [1, 2, 0], Passer),
    P1 #= Passer + 1,
    element(P1, [1, 2, 0], French).

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
