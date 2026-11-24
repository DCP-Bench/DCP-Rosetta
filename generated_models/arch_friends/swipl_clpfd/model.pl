% arch_friends: a SWI-Prolog model from DCP Rosetta.
%
% Harriet, upon returning from the mall, is happily describing her four shoe purchases to her friend Aurora. Aurora
% just loves the four different kinds of shoes that Harriet bought (ecru espadrilles, fuchsia flats, purple pumps, and
% suede sandals), but Harriet can't recall at which different store (Foot Farm, Heels in a Handcart, The Shoe Palace,
% or Tootsies) she got each pair. Can you help these two figure out the order in which Harriet bought each pair of
% shoes, and where she bought each?
%
% 1. Harriet bought fuchsia flats at Heels in a Handcart.
% 2. The store she visited just after buying her purple pumps was not Tootsies.
% 3. The Foot Farm was Harriet's second stop.
% 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields.
:- use_module(library(clpfd)).

% the stops are numbered 1 to 4; each shoe and each store is at one stop, the value of each variable is that stop
model(_Instance, Vars, [ecruespadrilles-Ecru, footfarm-FootFarm, fuchsiaflats-Fuchsia, heelsinahandcart-Handcart,
                        purplepumps-Purple, suedesandals-Suede, theshoepalace-Palace, tootsies-Tootsies]) :-
    Vars = [Ecru, Fuchsia, Purple, Suede, FootFarm, Handcart, Palace, Tootsies],
    Vars ins 1..4,
    % each shoe is bought at a different stop
    all_distinct([Ecru, Fuchsia, Purple, Suede]),
    % each store is visited at a different stop
    all_distinct([FootFarm, Handcart, Palace, Tootsies]),
    % Harriet bought fuchsia flats at Heels in a Handcart
    Fuchsia #= Handcart,
    % the store she visited just after buying her purple pumps was not Tootsies
    Tootsies #\= Purple + 1,
    % the Foot Farm was Harriet's second stop
    FootFarm #= 2,
    % two stops after leaving The Shoe Palace, Harriet bought her suede sandals
    Suede #= Palace + 2.

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
