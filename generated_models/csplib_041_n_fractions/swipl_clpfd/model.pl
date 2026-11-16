% csplib_041_n_fractions: a SWI-Prolog model from DCP Rosetta.
%
% Find distinct non-zero digits A, B, C, D, E, F, G, H and I such that A/BC + D/EF + G/HI = 1, where BC, EF and HI
% are the two-digit numbers formed by B and C, by E and F, and by H and I.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_, [A, B, C, D, E, F, G, H, I], ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I]) :-
    Digits = [A, B, C, D, E, F, G, H, I],
    Digits ins 1..9,
    % the nine digits are distinct
    all_distinct(Digits),
    % the two-digit numbers
    BC #= 10*B + C,
    EF #= 10*E + F,
    HI #= 10*H + I,
    % A/BC + D/EF + G/HI = 1, multiplied through by BC*EF*HI
    A*EF*HI + D*BC*HI + G*BC*EF #= BC*EF*HI.

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
