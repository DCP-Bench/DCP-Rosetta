% contracting_costs: a SWI-Prolog model from DCP Rosetta.
%
% A contractor planning the construction of a house has to pay six tradesmen in pairs: $1,100 to the paper hanger and
% the painter, $1,700 to the painter and the plumber, $1,100 to the plumber and the electrician, $3,300 to the
% electrician and the carpenter, $5,300 to the carpenter and the mason, and $3,200 to the mason and the painter. Find
% what each man charges for his services.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Vars,
      [paper_hanger-PaperHanger, painter-Painter, plumber-Plumber,
       electrician-Electrician, carpenter-Carpenter, mason-Mason]) :-
    Vars = [PaperHanger, Painter, Plumber, Electrician, Carpenter, Mason],
    % each charge is a positive amount no larger than the largest bill, 5300
    Vars ins 1..5300,
    % each pair of tradesmen is paid the sum of their charges
    PaperHanger + Painter #= 1100,
    Painter + Plumber #= 1700,
    Plumber + Electrician #= 1100,
    Electrician + Carpenter #= 3300,
    Carpenter + Mason #= 5300,
    Mason + Painter #= 3200.

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
