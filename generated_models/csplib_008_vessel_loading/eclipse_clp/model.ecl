% csplib_008_vessel_loading: an ECLiPSe model from DCP Rosetta.
%
% Vessel loading: supply vessels transport containers. The deck area is rectangular, and the
% containers are cuboid, laid out in a single layer, parallel to the sides of the deck. A
% container occupies the area from left to right across the width of the deck, and from bottom
% to top along its length, with right - left and top - bottom being its width and length, in
% that order or rotated by 90 degrees. All of these lie between 0 and the deck's size in that
% direction, and two containers may touch. Containers of some classes must keep a minimum
% distance, separation[a-1][b-1] for classes a and b, in at least one of the two directions.
% Decide whether the containers can be positioned on the deck without overlapping and without
% violating any separation constraint.
%
% Save this file as model.ecl. Download `csplib_008_vessel_loading.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_008_vessel_loading.json
%   eclipse -b model.ecl -e "run('csplib_008_vessel_loading_1.dat'), halt"

% Fields read from the data: deck_width and deck_length (the size of the deck across and along),
% n_containers (the number of containers), width and length (for each container, indexed from 0,
% its width and length), classes (for each container, indexed from 0, its class, numbered from 1)
% and separation (for classes a and b, the minimum distance separation[a-1][b-1]).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['left'-Lefts, 'right'-Rights, 'top'-Tops, 'bottom'-Bottoms]) :-
    memberchk(deck_width-DeckW, Instance),
    memberchk(deck_length-DeckL, Instance),
    memberchk(n_containers-N, Instance),
    memberchk(width-Widths, Instance),
    memberchk(length-Lengths, Instance),
    memberchk(classes-Classes, Instance),
    memberchk(separation-Separation, Instance),
    length(Lefts, N),
    length(Bottoms, N),
    length(Rots, N),
    % the left and bottom sides, and the rotation of each container (1 when rotated by 90 degrees)
    Lefts :: 0..DeckW,
    Bottoms :: 0..DeckL,
    Rots :: 0..1,
    % the container lies on the deck: its right side and top side are within the deck, and
    % its width and length are those of the container in its orientation
    ( for(I, 1, N), foreach(Right, Rights), foreach(Top, Tops),
      param(Lefts, Bottoms, Rots, Widths, Lengths, DeckW, DeckL) do
        nth1(I, Widths, W),
        nth1(I, Lengths, L),
        nth1(I, Lefts, Left),
        nth1(I, Bottoms, Bottom),
        nth1(I, Rots, Rot),
        Right #= Left + W + Rot * (L - W),
        Top #= Bottom + L + Rot * (W - L),
        Right #=< DeckW,
        Top #=< DeckL
    ),
    % any two containers do not overlap, and are at least the separation of their classes
    % apart in at least one of the two directions
    ( for(Row, 1, N), param(Lefts, Bottoms, Rights, Tops, Classes, Separation, N) do
        Row1 is Row + 1,
        nth1(Row, Classes, ClassI),
        nth1(Row, Lefts, LeftI), nth1(Row, Bottoms, BottomI),
        nth1(Row, Rights, RightI), nth1(Row, Tops, TopI),
        ( for(Col, Row1, N), param(Lefts, Bottoms, Rights, Tops, Classes, Separation,
                               ClassI, LeftI, BottomI, RightI, TopI) do
            nth1(Col, Classes, ClassJ),
            nth1(Col, Lefts, LeftJ), nth1(Col, Bottoms, BottomJ),
            nth1(Col, Rights, RightJ), nth1(Col, Tops, TopJ),
            nth1(ClassI, Separation, RowI),
            nth1(ClassJ, RowI, Gap),
            Apart1 #= (RightI + Gap #=< LeftJ),
            Apart2 #= (RightJ + Gap #=< LeftI),
            Apart3 #= (TopI + Gap #=< BottomJ),
            Apart4 #= (TopJ + Gap #=< BottomI),
            Apart1 + Apart2 + Apart3 + Apart4 #>= 1
        )
    ),
    flatten([Lefts, Bottoms, Rots], Vars).

:- lib(branch_and_bound).

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
