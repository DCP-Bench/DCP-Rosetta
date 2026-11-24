% de_bruijn_sequence: a SWI-Prolog model from DCP Rosetta.
%
% In combinatorial mathematics, a de Bruijn sequence of order n on a size-k alphabet A is a cyclic sequence in which
% every possible length-n string on A occurs exactly once as a substring. Such a sequence is denoted by B(k, n) and has
% length k^n.
%
% Save this file as model.pl. Download `de_bruijn_sequence.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('de_bruijn_sequence.json')" -t halt model.pl
%
% Data fields: base (the size k of the alphabet, whose symbols are 0 to k-1), n (the order: the length of the strings
% that must all occur).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Seq, [de_bruijn-Seq]) :-
    Base = Instance.base,
    N = Instance.n,
    M is Base ^ N,                       % the length of the cyclic sequence: one position per string
    Last is M - 1,
    Top is Base - 1,
    % Seq[I] is the symbol at position I, counted from 0
    length(Seq, M),
    Seq ins 0..Top,
    % the window starting at each position I reads the N symbols I, I+1, ... (cyclically) as one number
    numlist(0, Last, Starts),
    maplist({Seq, Base, N, M}/[I, Window]>>window(Seq, Base, N, M, I, Window), Starts, Windows),
    % every length-N string occurs exactly once: the M windows read M different numbers
    all_distinct(Windows).

% the number read from the N symbols starting at position I of the cyclic sequence, most significant first
window(Seq, Base, N, M, I, Number) :-
    Last is N - 1,
    numlist(0, Last, Offsets),
    maplist({Seq, Base, N, M, I}/[J, Term]>>(
                Position is ((I + J) mod M) + 1,
                Weight is Base ^ (N - 1 - J),
                nth1(Position, Seq, Symbol),
                Term #= Symbol * Weight),
            Offsets, Terms),
    sum(Terms, #=, Number).

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
