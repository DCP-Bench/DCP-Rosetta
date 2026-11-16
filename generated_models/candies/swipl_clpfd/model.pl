% candies: a SWI-Prolog model from DCP Rosetta.
%
% Children sit in a line, each with a rating score. Alice gives at least 1 candy to each child, and of two
% children sitting next to each other the one with the higher rating must get more candies. Minimise the total
% number of candies.
%
% Save this file as model.pl. Download `candies.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('candies.json')" -t halt model.pl
%
% Data fields: ratings (the rating score of each child in line order, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-Xs, z-Total], min(Total)) :-
    Ratings = Instance.ratings,
    length(Ratings, N),                    % the number of children
    length(Xs, N),                         % Xs[I] = candies for child I
    % every child gets at least one candy; an optimal allocation never needs more than N for one child
    Xs ins 1..N,
    % of two neighbours, the one with the higher rating gets more candies than the other
    neighbours(Ratings, Xs),
    % the total number of candies, to be minimised
    sum(Xs, #=, Total),
    Vars = [Total|Xs].

% for each pair of neighbours in line: the higher rating gets more candies, equal ratings give no rule
neighbours([R1, R2|Rs], [X1, X2|Xs]) :-
    (   R1 > R2 -> X1 #> X2
    ;   R1 < R2 -> X1 #< X2
    ;   true
    ),
    neighbours([R2|Rs], [X2|Xs]).
neighbours([_], [_]).

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
