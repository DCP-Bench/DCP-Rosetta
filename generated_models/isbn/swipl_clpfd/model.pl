% isbn: a SWI-Prolog model from DCP Rosetta.
%
% An ISBN-13 is a 13-digit number whose last digit is a check digit calculated from the first 12 digits: multiply the
% first 12 digits alternately by 1 and 3 (starting with 1), sum the products, and the check digit is
% (10 - (sum % 10)) % 10. Given 13 digits of an ISBN-13, where -1 stands for an unknown digit, find the unknown
% digits so that the resulting number is a valid ISBN-13. An ISBN-13 must start with 978 or 979. Give the complete
% valid ISBN as a list of 13 digits.
%
% Save this file as model.pl. Download `isbn.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('isbn.json')" -t halt model.pl
%
% Data fields: isbn_init (the 13 digits of the ISBN, indexed from 0; -1 marks an unknown digit).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(http/json)).

model(Instance, Vars, [isbn-Digits]) :-
    Init = Instance.isbn_init,
    length(Digits, 13),
    % each digit is 0 to 9
    Digits ins 0..9,
    % the digits that are known in the data keep their values
    maplist(keep_known, Init, Digits),
    % the ISBN starts with 978 or 979
    Digits = [D0, D1, D2|_],
    D0 #= 9,
    D1 #= 7,
    D2 #>= 8,
    D2 #=< 9,
    % the first 12 digits, multiplied alternately by 1 and 3 (starting with 1), are summed
    weighted_terms(Digits, 0, Terms),
    sum(Terms, #=, Sum),
    % the check digit (the 13th digit) is (10 - (Sum mod 10)) mod 10
    Digits = [_, _, _, _, _, _, _, _, _, _, _, _, Check],
    Remainder #= Sum mod 10,
    Check #= (10 - Remainder) mod 10,
    Vars = Digits.

% keep_known(+Given, ?Digit): a digit given as -1 is unknown, any other value is fixed
keep_known(Given, Digit) :-
    (   Given =:= -1
    ->  true
    ;   Digit #= Given
    ).

% weighted_terms(+Digits, +Position, -Terms): the products of the digits at positions 0 to 11 with their weights,
% weight 1 at even positions and 3 at odd positions (positions counted from 0)
weighted_terms([], _, []).
weighted_terms([Digit|Rest], Position, Terms) :-
    (   Position < 12
    ->  Weight is 1 + 2 * (Position mod 2),
        Terms = [Term|More],
        Term #= Weight * Digit,
        Next is Position + 1,
        weighted_terms(Rest, Next, More)
    ;   Terms = []
    ).

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
