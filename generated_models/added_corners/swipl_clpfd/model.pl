% added_corners: a SWI-Prolog model from DCP Rosetta.
%
% Enter the digits 1 through 8 into the eight positions around the edge of a 3 by 3 grid whose centre is empty, using
% each digit exactly once. The corners are circles (C) and the middles of the sides are squares (F):
%
%   C F C
%   F   F
%   C F C
%
% The number in each square must equal the sum of the numbers in the two circles adjoining it.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields.
:- use_module(library(clpfd)).

% the positions are listed in reading order: top left, top middle, top right, middle left, middle right,
% bottom left, bottom middle, bottom right
model(_Instance, Positions, [positions-Positions]) :-
    Positions = [TopLeft, TopMiddle, TopRight, MiddleLeft, MiddleRight, BottomLeft, BottomMiddle, BottomRight],
    Positions ins 1..8,
    % each digit from 1 to 8 is used exactly once
    all_distinct(Positions),
    % the square at the top middle is the sum of the two circles adjoining it
    TopMiddle #= TopLeft + TopRight,
    % the square at the middle left is the sum of the two circles adjoining it
    MiddleLeft #= TopLeft + BottomLeft,
    % the square at the middle right is the sum of the two circles adjoining it
    MiddleRight #= TopRight + BottomRight,
    % the square at the bottom middle is the sum of the two circles adjoining it
    BottomMiddle #= BottomLeft + BottomRight.

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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
