% zebra: a SWI-Prolog model from DCP Rosetta.
%
% The Zebra puzzle (sometimes referred to as Einstein's puzzle). There are five houses in a row, numbered from left to
% right. Each of the five houses is painted a different color, and has one inhabitant. The inhabitants are all of
% different nationalities, own different pets, drink different beverages and have different jobs.
% We know that: colors are yellow, green, red, white, and blue; nations of inhabitants are italy, spain, japan,
% england, and norway; pets are cat, zebra, bear, snails, and horse; drinks are milk, water, tea, coffee, and juice;
% jobs are painter, sculptor, diplomat, pianist, and doctor. The painter owns the horse. The diplomat drinks coffee.
% The one who drinks milk lives in the white house. The Spaniard is a painter. The Englishman lives in the red house.
% The snails are owned by the sculptor. The green house is immediately on the left of the red one. The Norwegian
% lives immediately on the right of the blue house. The doctor drinks milk. The diplomat is Japanese. The Norwegian
% owns the zebra. The green house is next to the white one. The horse is owned by the neighbor of the diplomat. The
% Italian either lives in the red, white or green house.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The problem has no data fields; the model reads none.
:- use_module(library(clpfd)).
:- use_module(library(apply)).

model(_Instance, Vars,
      [colors-Colors, nations-Nations, jobs-Jobs, pets-Pets, drinks-Drinks]) :-
    % each list gives the house (0..4) of the items of one category, in the order of the statement
    Colors = [_Yellow, Green, Red, White, Blue],
    Nations = [Italian, Spaniard, Japanese, Englishman, Norwegian],
    Jobs = [Painter, Sculptor, Diplomat, _Pianist, Doctor],
    Pets = [_Cat, Zebra, _Bear, Snails, Horse],
    Drinks = [Milk, _Water, _Tea, Coffee, _Juice],
    append([Colors, Nations, Jobs, Pets, Drinks], Vars),
    Vars ins 0..4,
    % the five items of a category are in five different houses
    maplist(all_distinct, [Colors, Nations, Jobs, Pets, Drinks]),
    % the painter owns the horse
    Painter #= Horse,
    % the diplomat drinks coffee
    Diplomat #= Coffee,
    % the one who drinks milk lives in the white house
    Milk #= White,
    % the Spaniard is a painter
    Spaniard #= Painter,
    % the Englishman lives in the red house
    Englishman #= Red,
    % the snails are owned by the sculptor
    Snails #= Sculptor,
    % the green house is immediately on the left of the red one
    Green + 1 #= Red,
    % the Norwegian lives immediately on the right of the blue house
    Norwegian #= Blue + 1,
    % the doctor drinks milk
    Doctor #= Milk,
    % the diplomat is Japanese
    Japanese #= Diplomat,
    % the Norwegian owns the zebra
    Norwegian #= Zebra,
    % the green house is next to the white one
    abs(Green - White) #= 1,
    % the horse is owned by the neighbour of the diplomat
    abs(Horse - Diplomat) #= 1,
    % the Italian lives in the red, white or green house
    Italian #= Red #\/ Italian #= White #\/ Italian #= Green.

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
