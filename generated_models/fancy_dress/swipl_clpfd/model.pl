% fancy_dress: a SWI-Prolog model from DCP Rosetta.
%
% Mr. Greenfan wants to give a dress party where the male guests must wear green dresses. The following rules are
% given: 1. If someone wears a green tie he has to wear a green shirt. 2. A guest who wears green socks or a green
% shirt must also wear a green tie or a green hat. 3. A guest wearing a green shirt or a green hat or who does not
% wear green socks must wear a green tie. 4. A guest who is not dressed according to rules 1-3 must pay a $11
% entrance fee. Mr Greenguest wants to participate but owns only a green shirt. He could buy a green tie for $10, a
% green hat (used) for $2 and green socks for $12. What is the cheapest solution for Mr Greenguest to participate?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Each choice is 0/1 (1 = worn or paid): tie T, hat H, shirt R, socks S, and the entrance fee N. The shirt is already
% owned, so wearing it costs nothing; the tie costs $10, the hat $2, the socks $12 and the fee $11.
model(_Instance, Vars, [t-T, h-H, r-R, s-S, n-N], min(10*T + 2*H + 12*S + 11*N)) :-
    Vars = [T, H, R, S, N, RulesHold],
    Vars ins 0..1,
    % RulesHold is 1 when rules 1 to 3 are all kept
    RulesHold #<==> ( (T #==> R)
                    #/\ ((S #\/ R) #==> (T #\/ H))
                    #/\ ((R #\/ H #\/ #\ S) #==> T) ),
    % rule 4: a guest who is not dressed according to rules 1 to 3 pays the entrance fee
    RulesHold #\/ N.

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
