% csplib_008_vessel_loading: a SWI-Prolog model from DCP Rosetta.
%
% Supply vessels transport containers from site to site. The deck area is rectangular. Containers are cuboid, and
% are laid out in a single layer, all parallel to the sides of the deck. The contents of the containers determine
% their class. Certain classes of containers are constrained to be separated by minimum distances either along the
% deck or across the deck. A container occupies the area from left to right across the width of the deck, and from
% bottom to top along its length, with right - left and top - bottom being its width and length, in that order or
% rotated by 90 degrees. All of these lie between 0 and the deck's size in that direction. Two containers may touch.
% The separation between the classes a and b is the distance that their containers must keep in at least one of the
% two directions. Decide whether all the containers can be positioned on the deck without overlapping and without
% violating any separation constraint.
%
% Save this file as model.pl. Download `csplib_008_vessel_loading.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_008_vessel_loading.json')" -t halt model.pl
%
% Data fields: deck_width and deck_length (the size of the deck across and along), width and length (for each
% container, its width and its length, lists indexed from 0), classes (the class of each container, numbered from
% 1), separation (for each pair of classes, the minimum distance their containers keep, indexed by class - 1).
:- use_module(library(clpfd)).

model(Instance, Vars, [left-Lefts, right-Rights, top-Tops, bottom-Bottoms]) :-
    DeckWidth = Instance.deck_width,
    DeckLength = Instance.deck_length,
    length(Instance.width, N),             % the number of containers
    % Turned[I] = 1 when container I is rotated by 90 degrees
    length(Turned, N),
    Turned ins 0..1,
    % each container has its width and its length, in this order or rotated; all of its sides lie on the deck
    maplist(box(DeckWidth, DeckLength), Instance.width, Instance.length, Turned, Boxes),
    % containers of classes a and b keep the distance separation[a-1][b-1] in at least one of the two directions
    % (with separation 0 they may touch but not overlap)
    each_pair(Boxes, Instance.classes, Pairs),
    maplist(separated(Instance.separation), Pairs),
    % implied: at every position along the deck the widths of the containers crossing it fit the deck's width,
    % and at every position across the deck their lengths fit the deck's length
    maplist(task_across, Boxes, TasksAcross),
    cumulative(TasksAcross, [limit(DeckLength)]),
    maplist(task_along, Boxes, TasksAlong),
    cumulative(TasksAlong, [limit(DeckWidth)]),
    maplist(arg(1), Boxes, Lefts),
    maplist(arg(2), Boxes, Rights),
    maplist(arg(3), Boxes, Bottoms),
    maplist(arg(4), Boxes, Tops),
    append([Turned, Lefts, Bottoms], Vars).

% box(Left, Right, Bottom, Top) of a container of width W and length L
box(DeckWidth, DeckLength, W, L, Turned, box(Left, Right, Bottom, Top)) :-
    Left in 0..DeckWidth,
    Right in 0..DeckWidth,
    Bottom in 0..DeckLength,
    Top in 0..DeckLength,
    Right #= Left + W + Turned * (L - W),
    Top #= Bottom + L + Turned * (W - L).

% a container as a task across the width (its length is the resource it uses) and along the length
task_across(box(Left, Right, Bottom, Top), task(Left, Width, Right, Length, 0)) :-
    Width #= Right - Left,
    Length #= Top - Bottom.
task_along(box(Left, Right, Bottom, Top), task(Bottom, Length, Top, Width, 0)) :-
    Width #= Right - Left,
    Length #= Top - Bottom.

% every pair of containers as boxA-classA-boxB-classB
each_pair([], [], []).
each_pair([Box|Boxes], [Class|Classes], Pairs) :-
    maplist(pair_with(Box-Class), Boxes, Classes, First),
    each_pair(Boxes, Classes, Rest),
    append(First, Rest, Pairs).

pair_with(Box1-Class1, Box2, Class2, Box1-Class1-Box2-Class2).

% one of the four ways of keeping the distance holds: left of, right of, below or above the other container
separated(Separation, Box1-Class1-Box2-Class2) :-
    nth1(Class1, Separation, Row),
    nth1(Class2, Row, Distance),
    Box1 = box(Left1, Right1, Bottom1, Top1),
    Box2 = box(Left2, Right2, Bottom2, Top2),
    Ways = [W1, W2, W3, W4],
    Ways ins 0..1,
    W1 #<==> (Right1 + Distance #=< Left2),
    W2 #<==> (Right2 + Distance #=< Left1),
    W3 #<==> (Top1 + Distance #=< Bottom2),
    W4 #<==> (Top2 + Distance #=< Bottom1),
    sum(Ways, #>=, 1).

:- use_module(library(http/json)).

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
