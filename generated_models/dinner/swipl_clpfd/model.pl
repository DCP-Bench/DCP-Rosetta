% dinner: a SWI-Prolog model from DCP Rosetta.
%
% We are going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children. Grandparents cost $3 for
% dinner, parents $2 and children $0.50. There must be 20 total people at dinner and it must cost $20.
% How many grandparents, parents and children are going to dinner?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Costs are counted in half dollars, so that a child's $0.50 is a whole number.
model(_Instance, [G, P, C], [grandparents-G, parents-P, children-C]) :-
    G in 1..6,                         % 1-6 grandparents
    P in 1..10,                        % 1-10 parents
    C in 1..40,                        % 1-40 children
    % there must be 20 people at dinner
    G + P + C #= 20,
    % and the dinner must cost $20, that is 40 half dollars
    6*G + 4*P + C #= 40.

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
