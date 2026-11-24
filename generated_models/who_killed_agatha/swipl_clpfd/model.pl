% who_killed_agatha: a SWI-Prolog model from DCP Rosetta.
%
% Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler, and Charles live in Dreadsbury Mansion, and
% are the only ones to live there. A killer always hates, and is no richer than his victim. Charles hates noone that
% Agatha hates. Agatha hates everybody except the butler. The butler hates everyone not richer than Aunt Agatha. The
% butler hates everyone whom Agatha hates. Noone hates everyone. Who killed Agatha?
%
% Save this file as model.pl. Download `who_killed_agatha.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('who_killed_agatha.json')" -t halt model.pl
%
% Data fields: names (the three names, a list indexed from 0: Agatha herself, the butler, Charles).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [killer-Killer]) :-
    Names = Instance.names,
    length(Names, N),
    Last is N - 1,
    % the people are numbered as in the names list: 0 Agatha herself, 1 the butler, 2 Charles
    Agatha = 0, Butler = 1, Charles = 2,
    numlist(0, Last, People),
    % Hates[I][J] = 1 when person I hates person J; Richer[I][J] = 1 when I is richer than J
    square(N, Hates),
    square(N, Richer),
    % Killed[I] = 1 when person I is the killer, and exactly one person is
    length(Killed, N),
    Killed ins 0..1,
    sum(Killed, #=, 1),
    scalar_product(People, Killed, #=, Killer),
    % richer than is read as irreflexive and antisymmetric: nobody is richer than himself, and of two people at most one
    % is richer than the other
    maplist({Richer}/[I]>>cell(Richer, I, I, 0), People),
    maplist({Richer, People}/[I]>>
                maplist({Richer, I}/[J]>>(cell(Richer, I, J, X), cell(Richer, J, I, Y), X + Y #=< 1), People),
            People),
    % a killer always hates the victim, Agatha, and is no richer than her
    maplist({Hates, Richer, Agatha}/[I, K]>>
                (cell(Hates, I, Agatha, H), cell(Richer, I, Agatha, R), K #==> (H #= 1 #/\ R #= 0)),
            People, Killed),
    % Charles hates nobody that Agatha hates
    maplist({Hates, Agatha, Charles}/[I]>>
                (cell(Hates, Agatha, I, A), cell(Hates, Charles, I, C), A #= 1 #==> C #= 0),
            People),
    % Agatha hates everybody except the butler
    cell(Hates, Agatha, Agatha, 1),
    cell(Hates, Agatha, Charles, 1),
    cell(Hates, Agatha, Butler, 0),
    % the butler hates everyone not richer than Aunt Agatha
    maplist({Hates, Richer, Agatha, Butler}/[I]>>
                (cell(Richer, I, Agatha, R), cell(Hates, Butler, I, B), R #= 0 #==> B #= 1),
            People),
    % the butler hates everyone whom Agatha hates
    maplist({Hates, Agatha, Butler}/[I]>>
                (cell(Hates, Agatha, I, A), cell(Hates, Butler, I, B), A #= 1 #==> B #= 1),
            People),
    % noone hates everyone
    maplist({Last}/[Row]>>sum(Row, #=<, Last), Hates),
    append(Hates, HatesFlat),
    append(Richer, RicherFlat),
    append([Killed, HatesFlat, RicherFlat], Vars).

square(N, Rows) :-
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows).

% Cell is the entry in row I, column J of Rows (0-based, I and J ground).
cell(Rows, I, J, Cell) :-
    nth0(I, Rows, Row),
    nth0(J, Row, Cell).

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
