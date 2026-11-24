% session2_color_simple: a SWI-Prolog model from DCP Rosetta.
%
% We want to assign a different colour to the following countries: Belgium, Denmark, France, Germany, Netherlands and
% Luxembourg. Two neighbouring countries cannot have the same colour. You can use integers starting from 1 to represent
% the colours. Find a colouring that minimizes the number of colours used.
%
% Save this file as model.pl. Download `session2_color_simple.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session2_color_simple.json')" -t halt model.pl
%
% Data fields: graph (the neighbouring pairs of countries, each a pair of country numbers, 1-based, in the order of the
% countries listed above; the list is indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [colors-Colors], min(Used)) :-
    Graph = Instance.graph,
    NumCountries = 6,                      % Belgium, Denmark, France, Germany, Netherlands, Luxembourg
    length(Colors, NumCountries),          % Colors[I] is the colour of country I + 1
    Vars = [Used|Colors],
    % colours are integers from 1 to the number of countries
    Colors ins 1..NumCountries,
    Used in 1..NumCountries,
    % neighbouring countries have different colours
    maplist({Colors}/[Edge]>>different_colours(Colors, Edge), Graph),
    % Used is the number of colours used: the largest colour on the map
    maplist({Used}/[Colour]>>(Used #>= Colour), Colors).

% different_colours(+Colors, +Edge): the two countries of Edge, numbered from 1, have different colours.
different_colours(Colors, [I, J]) :-
    nth1(I, Colors, Here),
    nth1(J, Colors, There),
    Here #\= There.

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
