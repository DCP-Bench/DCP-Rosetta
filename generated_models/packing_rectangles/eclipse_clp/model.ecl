% packing_rectangles: an ECLiPSe model from DCP Rosetta.
%
% The rectangular packing problem involves placing a set of rectangular items into a larger rectangular area such that
% no items overlap and all items are within the boundaries of the larger area. The objective is to minimize the total
% area of the larger rectangle required to pack all the items. Given the widths and heights of the items, determine
% their positions within the larger rectangle while ensuring no overlap and minimizing the total area. The items keep
% the widths and heights given, along the horizontal and the vertical axes.
%
% Save this file as model.ecl. Download `packing_rectangles.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py packing_rectangles.json
%   eclipse -b model.ecl -e "run('packing_rectangles_1.dat'), halt"
%
% The data fields: widths[I] and heights[I] are the width and the height of item I, lists indexed from 0 as in the JSON.

:- lib(ic).
:- lib(branch_and_bound).

% Outputs: pos_x[I] and pos_y[I] are the position of the lower left corner of item I; total_x and total_y are the
% width and the height of the larger rectangle.
model(Instance, Vars, [pos_x-Xs, pos_y-Ys, total_x-TotalX, total_y-TotalY], min(Area)) :-
    memberchk(widths-Widths, Instance),
    memberchk(heights-Heights, Instance),
    total_of(Widths, SumWidths),
    total_of(Heights, SumHeights),
    length(Widths, NumItems),
    length(Xs, NumItems),
    length(Ys, NumItems),

    % the positions lie within the sum of the sizes, and the larger rectangle is at most that wide and high
    Xs :: 0..SumWidths,
    Ys :: 0..SumHeights,
    TotalX :: 0..SumWidths,
    TotalY :: 0..SumHeights,

    % every item lies within the larger rectangle
    ( foreach(X, Xs), foreach(W, Widths), param(TotalX) do
        X + W #=< TotalX
    ),
    ( foreach(Y, Ys), foreach(H, Heights), param(TotalY) do
        Y + H #=< TotalY
    ),

    % no two items overlap: one of them lies to the left of the other, or below it
    make_items(Xs, Ys, Widths, Heights, Items),
    no_overlaps(Items),

    % the area of the larger rectangle, which is to be as small as possible
    Area #= TotalX * TotalY,

    app(Xs, Ys, T),
    app(T, [TotalX, TotalY], Vars).

% the sum of a list of numbers
total_of([], 0).
total_of([X | Xs], S) :-
    total_of(Xs, S0),
    S is X + S0.

% an item: its position and its size
make_items([], [], [], [], []).
make_items([X | Xs], [Y | Ys], [W | Ws], [H | Hs], [item(X, Y, W, H) | Items]) :-
    make_items(Xs, Ys, Ws, Hs, Items).

% every pair of items does not overlap
no_overlaps([]).
no_overlaps([I | Items]) :-
    ( foreach(J, Items), param(I) do
        no_overlap(I, J)
    ),
    no_overlaps(Items).

no_overlap(item(X1, Y1, W1, H1), item(X2, Y2, W2, H2)) :-
    (   X1 + W1 #=< X2
    or  X2 + W2 #=< X1
    or  Y1 + H1 #=< Y2
    or  Y2 + H2 #=< Y1
    ).

app([], Ys, Ys).
app([X | Xs], Ys, [X | Zs]) :-
    app(Xs, Ys, Zs).

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

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
