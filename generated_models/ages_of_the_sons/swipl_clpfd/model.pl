% ages_of_the_sons: a SWI-Prolog model from DCP Rosetta.
%
% An old man asked a mathematician to guess the ages of his three sons.
%
% Old man said: "The product of their ages is 36."
% Mathematician said: "I need more information."
%
% Old man said: "Over there you can see a building. The sum of their ages equals the number of the windows in that
% building."
% After a short while the mathematician said: "I need more information."
%
% Old man said: "The oldest son has blue eyes."
% Mathematician said: "I got it."
%
% What are the ages of the three sons of the old man?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields.
:- use_module(library(clpfd)).

% the three ages, oldest first, are A1, A2, A3
model(_Instance, Vars, ['A1'-A1, 'A2'-A2, 'A3'-A3]) :-
    % the ages are one of the triples, oldest first, whose product is 36
    sorted_triples(Triples),
    [A1, A2, A3] ins 1..36,
    tuples_in([[A1, A2, A3]], Triples),
    Sum #= A1 + A2 + A3,
    length(Triples, N),
    length(Shared, N), Shared ins 0..1,
    length(Unique, N), Unique ins 0..1,
    % the product alone does not fix the ages (several triples have product 36), so the mathematician needed more
    % information; the sum is the number of windows, and the mathematician still needs more information, so several
    % triples must share the sum
    maplist(same_sum(Sum), Triples, Shared),
    sum(Shared, #>=, 2),
    % the oldest son has blue eyes, so the oldest son is a single one: he is older than the second son
    A1 #> A2,
    % the mathematician got it, so exactly one triple with this sum has a single oldest son
    maplist(single_oldest_with_sum(Sum), Triples, Unique),
    sum(Unique, #=, 1),
    append([[A1, A2, A3], Shared, Unique], Vars).

% every triple of ages, oldest first, whose product is 36
sorted_triples(Triples) :-
    findall([A, B, C], (between(1, 36, A), between(1, A, B), between(1, B, C), A * B * C =:= 36), Triples).

% Same is 1 when the triple [X, Y, Z] has the given sum
same_sum(Sum, [X, Y, Z], Same) :-
    Same #<==> (Sum #= X + Y + Z).

% Ok is 1 when the triple [X, Y, Z] has the given sum and a single oldest son (X is older than Y)
single_oldest_with_sum(Sum, [X, Y, Z], Ok) :-
    Ok #<==> ((Sum #= X + Y + Z) #/\ (X #> Y)).

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
