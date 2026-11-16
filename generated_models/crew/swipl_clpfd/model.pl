% crew: a SWI-Prolog model from DCP Rosetta.
%
% Assign flight attendants to flights. Each flight needs a certain number of cabin crew, and they have to speak
% certain languages. Every cabin crew member has at least two flights off after an attended flight, so nobody
% attends more than one of any three consecutive flights.
%
% Save this file as model.pl. Download `crew.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('crew.json')" -t halt model.pl
%
% Data fields: attributes (for each person, five 0/1 values: steward, hostess, speaks French, speaks Spanish,
% speaks German), required_crew (for each flight, six numbers: the number of cabin crew, then the numbers of
% stewards, hostesses, French, Spanish and German speakers needed). Both lists are indexed from 0.
:- use_module(library(clpfd)).

model(Instance, Crew, [crew-Crew]) :-
    Attributes = Instance.attributes,
    RequiredCrew = Instance.required_crew,
    length(Attributes, NumPersons),
    length(RequiredCrew, NumFlights),
    % Crew[F][P] is 1 when person P is assigned to flight F
    length(Crew, NumFlights),
    maplist({NumPersons}/[Row]>>(length(Row, NumPersons), Row ins 0..1), Crew),
    % the attribute columns: one list of 0/1 values per attribute, over the persons
    transpose(Attributes, Columns),
    % each flight has exactly the required number of cabin crew, with at least the required number of each attribute
    maplist(flight_staffed(Columns), Crew, RequiredCrew),
    % nobody attends more than one of any three consecutive flights
    no_three_in_a_row(Crew).

% the row of a flight has the crew size, and each attribute column meets its minimum over that row
flight_staffed(Columns, Row, [Size|Minimums]) :-
    sum(Row, #=, Size),
    maplist(attribute_met(Row), Columns, Minimums).

attribute_met(Row, Column, Minimum) :-
    scalar_product(Column, Row, #>=, Minimum).

no_three_in_a_row([F1, F2, F3|Rest]) :-
    maplist(at_most_one, F1, F2, F3),
    no_three_in_a_row([F2, F3|Rest]).
no_three_in_a_row(Flights) :-
    length(Flights, Len),
    Len < 3.

at_most_one(A, B, C) :-
    A + B + C #=< 1.

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
