% four_islands: a SWI-Prolog model from DCP Rosetta.
%
% A tiny nation in the South Pacific has four islands, A, B, C and D, joined by bridges: A and B lie on top, C and D
% below, with bridges A-B, A-C, B-D and C-D. So A is north of C, B is north of D, A is west of B and C is west of D.
% The islands are Pwana, Quero, Rayou and Skern. Each has a different primary export (alabaster, bananas, coconuts,
% durian fruit) and a different tourist attraction (resort hotel, ice skating rink, jai alai stadium, koala
% preserve). Clues: 1. the island with the koala preserve is due south of Pwana; 2. the island exporting alabaster
% is due west of Quero; 3. the island with the resort hotel is due east of the island exporting durian fruit;
% 4. Skern and the island with the jai alai stadium are connected by a north-south bridge; 5. Rayou and the island
% exporting bananas are connected by an east-west bridge; 6. the islands with the ice skating rink and the jai alai
% stadium are not connected by a bridge. Find the export and attraction of each island, and the map position of each.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% No data fields: the model reads nothing from the data. Map positions are 0 for A, 1 for B, 2 for C and 3 for D.
:- use_module(library(clpfd)).

model(_Instance, [Island, Export, Attraction], [island-Island, export-Export, attraction-Attraction]) :-
    length(Island, 4),
    length(Export, 4),
    length(Attraction, 4),
    Island = [Pwana, Quero, Rayou, Skern],
    Export = [Alabaster, Bananas, _Coconuts, Durian],
    Attraction = [Hotel, Rink, JaiAlai, Koala],
    append([Island, Export, Attraction], All),
    All ins 0..3,
    maplist(all_distinct, [Island, Export, Attraction]),
    % clue 1: the koala preserve is due south of Pwana
    tuples_in([[Koala, Pwana]], [[2,0],[3,1]]),
    % clue 2: the alabaster island is due west of Quero
    tuples_in([[Alabaster, Quero]], [[0,1],[2,3]]),
    % clue 3: the resort hotel is due east of the durian fruit island
    tuples_in([[Hotel, Durian]], [[1,0],[3,2]]),
    % clue 4: Skern and the jai alai stadium are connected by a north-south bridge
    tuples_in([[Skern, JaiAlai]], [[0,2],[2,0],[1,3],[3,1]]),
    % clue 5: Rayou and the banana island are connected by an east-west bridge
    tuples_in([[Rayou, Bananas]], [[0,1],[1,0],[2,3],[3,2]]),
    % clue 6: the ice skating rink and the jai alai stadium are not connected by a bridge
    tuples_in([[Rink, JaiAlai]], [[0,3],[3,0],[1,2],[2,1]]).

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
