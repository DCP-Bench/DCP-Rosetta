% four_islands: an ECLiPSe model from DCP Rosetta.
%
% A tiny nation in the South Pacific contains four islands connected by bridges. Each of the four islands (Pwana, Quero,
% Rayou and Skern) boasts a different primary export (alabaster, bananas, coconuts and durian fruit) and a different
% tourist attraction (hotel, ice skating rink, jai alai stadium and koala preserve). Find the name, export and tourist
% attraction of each island on the map. The islands A, B, C, D are placed on the map as
%   (A) -- (B)
%    |      |
%   (C) -- (D)
% so A is north of C, C is west of D, and so on. The clues are: the island noted for its koala preserve is due south
% of Pwana; the island with the largest alabaster quarry is due west of Quero; the island with the resort hotel is due
% east of the one that exports durian fruit; Skern and the island with the jai alai stadium are connected by a
% north-south bridge; Rayou and the island that exports bananas are connected by an east-west bridge; the islands noted
% for the ice skating rink and for the jai alai stadium are not connected by a bridge.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% A map position P is 2*Row + Col, with Row 0 for the north pair and Col 0 for the west. The row and the column are
% separate variables tied to P by a linear equation, since ic raises an instantiation fault on // and mod applied to a
% variable.
coord(P, Row, Col) :-
    Row :: 0..1,
    Col :: 0..1,
    P #= 2*Row + Col.

% X is due south of Y: one row further south, same column.
due_south(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY + 1,
    CX #= CY.

% X is due west of Y: same row, one column further west.
due_west(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY,
    CX #= CY - 1.

% X is due east of Y: same row, one column further east.
due_east(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY,
    CX #= CY + 1.

% X and Y are connected by a north-south bridge: same column, different row.
ns_bridge(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    CX #= CY,
    RX #\= RY.

% X and Y are connected by an east-west bridge: same row, different column.
ew_bridge(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #= RY,
    CX #\= CY.

% X and Y are not connected by a bridge: they lie on a diagonal.
not_bridged(X, Y) :-
    coord(X, RX, CX), coord(Y, RY, CY),
    RX #\= RY,
    CX #\= CY.

% The variables are the map positions (0 to 3) of the islands Pwana, Quero, Rayou and Skern, of the alabaster, bananas,
% coconuts and durian fruit islands, and of the resort hotel, ice skating rink, jai alai stadium and koala preserve.
model(_Instance, Vars, Outputs) :-
    Vars = [Pwana, Quero, Rayou, Skern, Alabaster, Bananas, Coconuts, Durian,
            Hotel, Rink, JaiAlai, Koala],
    Vars :: 0..3,

    % each island has a different name, a different export and a different attraction
    alldifferent([Pwana, Quero, Rayou, Skern]),
    alldifferent([Alabaster, Bananas, Coconuts, Durian]),
    alldifferent([Hotel, Rink, JaiAlai, Koala]),

    % the island noted for its koala preserve is due south of Pwana
    due_south(Koala, Pwana),

    % the island with the largest alabaster quarry is due west of Quero
    due_west(Alabaster, Quero),

    % the island with the resort hotel is due east of the one that exports durian fruit
    due_east(Hotel, Durian),

    % Skern and the island with the jai alai stadium are connected by a north-south bridge
    ns_bridge(Skern, JaiAlai),

    % Rayou and the island that exports bananas are connected by an east-west bridge
    ew_bridge(Rayou, Bananas),

    % the islands noted for the ice skating rink and for the jai alai stadium are not connected by a bridge
    not_bridged(Rink, JaiAlai),

    % 'export' is a prefix operator in ECLiPSe, so the pair is written in functional form
    Outputs = [-('island', [Pwana, Quero, Rayou, Skern]),
               -('export', [Alabaster, Bananas, Coconuts, Durian]),
               -('attraction', [Hotel, Rink, JaiAlai, Koala])].

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
