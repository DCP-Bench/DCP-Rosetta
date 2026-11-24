% packing_rectangles: a SWI-Prolog model from DCP Rosetta.
%
% The rectangular packing problem involves placing a set of rectangular items into a larger rectangular area such that
% no items overlap and all items are within the boundaries of the larger area. Given the widths and heights of the
% items, determine their positions within the larger rectangle, without rotating the items, so that the total area of
% the larger rectangle is as small as possible.
%
% Save this file as model.pl. Download `packing_rectangles.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('packing_rectangles.json')" -t halt model.pl
%
% Data fields: widths and heights (the width and the height of each item, lists indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Vars, [pos_x-Xs, pos_y-Ys, total_x-TotalX, total_y-TotalY], min(Area)) :-
    Widths = Instance.widths,
    Heights = Instance.heights,
    length(Widths, N),
    sum_list(Widths, SumWidths),
    sum_list(Heights, SumHeights),
    max_list(Widths, WidestItem),
    max_list(Heights, TallestItem),
    % the enclosing rectangle is at least as wide as the widest item, and at most as wide as all items side by side
    TotalX in WidestItem..SumWidths,
    % the enclosing rectangle is at least as high as the tallest item, and at most as high as all items stacked
    TotalY in TallestItem..SumHeights,
    % Xs[I], Ys[I] are the lower left corner of item I, counted from 0
    length(Xs, N),
    Xs ins 0..SumWidths,
    length(Ys, N),
    Ys ins 0..SumHeights,
    % every item lies completely inside the enclosing rectangle
    maplist({TotalX}/[X, W]>>(X + W #=< TotalX), Xs, Widths),
    maplist({TotalY}/[Y, H]>>(Y + H #=< TotalY), Ys, Heights),
    % no two items overlap
    rectangles(Xs, Widths, Ys, Heights, Rectangles),
    disjoint2(Rectangles),
    % the area of the enclosing rectangle, to be minimised
    Area #= TotalX * TotalY,
    append([Xs, Ys, [TotalX, TotalY, Area]], Vars).

% rectangles(+Xs, +Widths, +Ys, +Heights, -Rectangles): each item as the f(X, W, Y, H) term disjoint2/1 expects
rectangles([], [], [], [], []).
rectangles([X|Xs], [W|Ws], [Y|Ys], [H|Hs], [f(X, W, Y, H)|Rectangles]) :-
    rectangles(Xs, Ws, Ys, Hs, Rectangles).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
