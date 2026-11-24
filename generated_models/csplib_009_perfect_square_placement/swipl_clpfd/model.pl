% csplib_009_perfect_square_placement: a SWI-Prolog model from DCP Rosetta.
%
% The perfect square placement problem (also called the squared square problem) is to pack a set of squares with
% given integer sizes into a bigger square, so that no squares overlap each other and all square borders are parallel
% to the border of the big square. The sum of the square surfaces is equal to the surface of the packing square, so
% that there is no spare capacity.
%
% Save this file as model.pl. Download `csplib_009_perfect_square_placement.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_009_perfect_square_placement.json')" -t halt model.pl
%
% Data fields: base (the side of the big square), sides (the side of each square, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [x_coords-Xs, y_coords-Ys]) :-
    Base = Instance.base,
    Sides = Instance.sides,
    length(Sides, Count),
    length(Xs, Count),
    length(Ys, Count),
    % square I has its lower left corner at (Xs[I], Ys[I])
    Xs ins 0..Base,
    Ys ins 0..Base,
    % every square lies inside the big square, across and along
    maplist(inside(Base), Xs, Sides),
    maplist(inside(Base), Ys, Sides),
    % no two squares overlap
    maplist(rectangle, Xs, Ys, Sides, Rectangles),
    disjoint2(Rectangles),
    Vars = [Xs, Ys].

% a square starting at Start with the given side ends within the big square of side Base
inside(Base, Start, Side) :-
    Start + Side #=< Base.

% the square as a rectangle f(X, Width, Y, Height)
rectangle(X, Y, Side, f(X, Side, Y, Side)).

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
