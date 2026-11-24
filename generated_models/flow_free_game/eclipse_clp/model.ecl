% flow_free_game: an ECLiPSe model from DCP Rosetta.
%
% Connect matching colors with pipe to create a flow. Pair all colors, and cover the entire board to solve each puzzle in
% Flow Free. But watch out, pipes will break if they cross or overlap! The cells of the board with a value of 0
% are empty and need to be filled with a color. Cells are connected horizontally and vertically: a numbered cell has
% exactly one neighbour of its own color, and a filled cell has exactly two.
%
% Save this file as model.ecl. Download `flow_free_game.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py flow_free_game.json
%   eclipse -b model.ecl -e "run('flow_free_game_1.dat'), halt"
%
% The data fields: board is the grid of the board, one list per row, with the colour of each numbered cell and 0 for
% an empty cell.

:- lib(ic).
:- lib(listut).

% B is the colour of every cell (1..K, K being the largest clue); Ds[P] is the distance of cell P from the end of its pipe.
model(Instance, Vars, ['B'-Rows]) :-
    memberchk(board-Board, Instance),
    length(Board, R),
    Board = [Row1 | _],
    length(Row1, C),
    N is R * C,
    flatten(Board, Clues),
    max_of(Clues, K),
    cell_colours(Clues, K, Bs),
    length(Ds, N),
    Ds :: 0..N-1,
    cell_rules(1, N, Clues, Bs, Ds, R, C),
    rows(Bs, C, Rows),
    append(Bs, Ds, Vars).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

max_of([X], X).
max_of([X|Xs], M) :-
    max_of(Xs, M0),
    M is max(X, M0).

% a numbered cell keeps its colour; an empty cell takes a colour from 1 to K
cell_colours([], _, []).
cell_colours([V|Vs], K, [B|Bs]) :-
    ( V > 0 -> B = V ; B :: 1..K ),
    cell_colours(Vs, K, Bs).

% Every cell belongs to one pipe. A numbered cell is a pipe end: one neighbour of its colour, distance 0. Any other cell
% has two neighbours of its colour and a predecessor, a neighbour of its colour one step closer to the end. Distances
% strictly decrease along predecessors, so every pipe reaches a numbered end and no loop floats free of the ends.
cell_rules(P, N, _, _, _, _, _) :-
    P > N, !.
cell_rules(P, N, Clues, Bs, Ds, R, C) :-
    nth1(P, Clues, V),
    nth1(P, Bs, Bp),
    nth1(P, Ds, Dp),
    neighbours(P, R, C, Ns),
    neighbour_rules(Ns, Bp, Dp, Bs, Ds, N, Es, Ps),
    (   V > 0 ->
        % a numbered cell is a pipe end: one neighbour of its colour, distance 0
        sum(Es) #= 1,
        Dp #= 0
    ;   % any other cell: two neighbours of its colour, and a predecessor
        sum(Es) #= 2,
        Dp #>= 1,
        sum(Ps) #>= 1
    ),
    P1 is P + 1,
    cell_rules(P1, N, Clues, Bs, Ds, R, C).

% For each neighbour Q of cell P: E is 1 when Q has the same colour, and Pq is 1 when Q is the predecessor of P (same
% colour and exactly one step closer to the end). A cell is at most one step further than a neighbour of its colour.
neighbour_rules([], _, _, _, _, _, [], []).
neighbour_rules([Q|Qs], Bp, Dp, Bs, Ds, N, [E|Es], [Pq|Ps]) :-
    nth1(Q, Bs, Bq),
    nth1(Q, Ds, Dq),
    E #= (Bp #= Bq),
    Dp #=< Dq + 1 + N*(1 - E),
    Pq :: 0..1,
    F #= (Dq #= Dp - 1),
    Pq #=< E,
    Pq #=< F,
    Pq #>= E + F - 1,
    neighbour_rules(Qs, Bp, Dp, Bs, Ds, N, Es, Ps).

% 1-based indices of the cells next to cell P on an R x C board
neighbours(P, R, C, Ns) :-
    I is (P-1) // C + 1,
    J is (P-1) mod C + 1,
    findall(Q, adjacent(I, J, R, C, Q), Ns).

adjacent(I, J, R, C, Q) :-
    member(DI-DJ, [(-1)-0, 1-0, 0-(-1), 0-1]),
    I2 is I + DI,
    J2 is J + DJ,
    I2 >= 1, I2 =< R,
    J2 >= 1, J2 =< C,
    Q is (I2-1)*C + J2.

% rows(+Bs, +C, -Rows): the flat list of cells cut into rows of C cells
rows([], _, []).
rows(Bs, C, [Row|Rows]) :-
    Bs = [_|_],
    length(Row, C),
    append(Row, Rest, Bs),
    rows(Rest, C, Rows).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

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
