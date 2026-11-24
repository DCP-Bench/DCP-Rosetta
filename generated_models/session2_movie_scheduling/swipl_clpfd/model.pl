% session2_movie_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% You are a highly-in-demand actor, presented with offers to star in n different movie projects under development. Each
% offer comes with the first and last day of filming. To take a job, you must be available throughout its entire
% period, so you cannot accept two jobs whose periods overlap. Each film pays the same fee, so you want the largest set
% of jobs such that no two of them conflict. Which movies are accepted?
%
% Save this file as model.pl. Download `session2_movie_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session2_movie_scheduling.json')" -t halt model.pl
%
% Data fields: movies (the offers, in order, each a list [title, first day, last day]; the list is indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

model(Instance, Vars, [selected_movies-Selected], max(Watched)) :-
    Movies = Instance.movies,
    length(Movies, NumMovies),
    length(Selected, NumMovies),           % Selected[I] is 1 when offer I is accepted, 0 otherwise
    Selected ins 0..1,
    % the number of films accepted, to be as large as possible
    sum(Selected, #=, Watched),
    Watched in 0..NumMovies,
    Vars = [Watched|Selected],
    % pair each offer with its days and its selection flag
    maplist(film, Movies, Selected, Films),
    % two offers whose days overlap cannot both be accepted
    no_overlapping_pairs(Films).

% film(+Movie, ?Selected, -Film): Film holds the first day, last day and selection flag of a movie [title, first, last].
film([_Title, First, Last], Selected, film(First, Last, Selected)).

% no_overlapping_pairs(+Films): no two films whose days overlap are both accepted.
no_overlapping_pairs([]).
no_overlapping_pairs([Film|Films]) :-
    maplist(no_overlap(Film), Films),
    no_overlapping_pairs(Films).

% no_overlap(+Film1, +Film2): the days of the two films overlap only when they share a day, and then not both are accepted.
no_overlap(film(First1, Last1, Sel1), film(First2, Last2, Sel2)) :-
    (   First1 =< Last2,
        First2 =< Last1
    ->  Sel1 + Sel2 #=< 1
    ;   true
    ).

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
