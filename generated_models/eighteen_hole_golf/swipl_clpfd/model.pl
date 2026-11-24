% eighteen_hole_golf: a SWI-Prolog model from DCP Rosetta.
%
% Generate an 18-hole golf course where each hole has a length of 3, 4, or 5, and the total length of the course is 72.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Holes, [holes-Holes]) :-
    length(Holes, 18),                 % the 18 holes of the course
    Holes ins 3..5,                    % each hole has a length of 3, 4 or 5
    sum(Holes, #=, 72).                % the total length of the course is 72

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
