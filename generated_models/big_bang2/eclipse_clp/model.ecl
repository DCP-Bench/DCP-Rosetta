% big_bang2: an ECLiPSe model from DCP Rosetta.
%
% Nontransitive dice: find a set of five dice, each with six integer faces from 1 to 12 (faces may repeat), so that the
% dominance relationships between the dice are those of Rock-Paper-Scissors extended by Lizard and Spock. Rock crushes
% Scissors and Lizard; Paper covers Rock and disproves Spock; Scissors cuts Paper and decapitates Lizard; Lizard eats Paper
% and poisons Spock; Spock vaporizes Rock and smashes Scissors. A die A beats a die B when A has a strictly larger face than B
% in more than half of the 36 pairs of faces. Find the dice as a list of lists, in the order Rock, Paper, Scissors, Lizard,
% Spock.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(gfd).

% The model reads no data. Dice lists the faces of each die, in the order Rock, Paper, Scissors, Lizard, Spock.
model(_Instance, Vars, [dice-Dice]) :-
    Dice = [Rock, Paper, Scissors, Lizard, Spock],
    % each die has six faces, each a whole number from 1 to 12
    ( foreach(Die, Dice) do length(Die, 6), Die :: 1..12 ),
    % the faces of a die are a set: they are listed in ascending order, which breaks the symmetry
    ( foreach(Die, Dice) do ascending(Die) ),
    % the ten beats relationships: the first die beats the second
    beats(Rock, Scissors), beats(Rock, Lizard),
    beats(Paper, Rock), beats(Paper, Spock),
    beats(Scissors, Paper), beats(Scissors, Lizard),
    beats(Lizard, Paper), beats(Lizard, Spock),
    beats(Spock, Rock), beats(Spock, Scissors),
    % labelling order: Rock, Scissors, Lizard, Paper, Spock, so that each die is fixed
    % next to the dice it is compared with
    flatten([Rock, Scissors, Lizard, Paper, Spock], Vars).

ascending([X, Y | Rest]) :- X #=< Y, ascending([Y | Rest]).
ascending([_]).

% die A beats die B when A has a strictly larger face than B in at least 19 of the 36 pairs of faces
beats(A, B) :-
    ( foreach(X, A), foreach(Row, Rows), param(B) do
        ( foreach(Y, B), foreach(Win, Row), param(X) do
            Win :: 0..1,
            ( X #> Y ) <=> ( Win #= 1 )
        )
    ),
    flatten(Rows, Wins),
    sum(Wins) #>= 19.

search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

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
