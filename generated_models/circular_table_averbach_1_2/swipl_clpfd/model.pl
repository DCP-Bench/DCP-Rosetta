% circular_table_averbach_1_2: a SWI-Prolog model from DCP Rosetta.
%
% Three players X, Y and Z of different nationalities (American, English, French) sit around a circular table playing
% Hearts. Each passed three cards to the person on their right. Y passed three hearts to the American, and X passed
% the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman. Determine the
% nationality of each person. The seats are numbered 0, 1 and 2, and seat 1 is to the right of seat 0, seat 2 to the
% right of seat 1, and so on round the table.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Vars, [x-X, y-Y, z-Z, american-American, english-English, french-French]) :-
    Vars = [X, Y, Z, American, English, French],
    Vars ins 0..2,                         % seats 0, 1 and 2
    % the three players sit in different seats
    all_different([X, Y, Z]),
    % the three nationalities are held by different seats
    all_different([American, English, French]),
    % the seat to the right of seat B is (B + 1) mod 3; Y passed to the American, so the American sits to the right of Y
    American #= (Y + 1) mod 3,
    % X passed to the person who passed to the Frenchwoman, who sits to the left of her: the seat to the right of X
    % is the seat to the left of the Frenchwoman
    X #= (French + 1) mod 3.

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
