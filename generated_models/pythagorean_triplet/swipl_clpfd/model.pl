% pythagorean_triplet: a SWI-Prolog model from DCP Rosetta.
%
% A Pythagorean triplet is a set of three natural numbers a, b and c for which a^2 + b^2 = c^2. The order of a and b
% does not matter. There exists exactly one Pythagorean triplet for which a + b + c = 1000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The model reads no data fields: the problem has fixed numbers only.
:- use_module(library(clpfd)).
:- use_module(library(http/json)).

model(_Instance, [A, B, C], [a-A, b-B, c-C]) :-
    % a, b and c are natural numbers no larger than 1000
    [A, B, C] ins 1..1000,
    % a + b + c = 1000
    A + B + C #= 1000,
    % a^2 + b^2 = c^2
    A*A + B*B #= C*C,
    % the order of a and b does not matter, so a is the smaller of the two
    A #< B.

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
