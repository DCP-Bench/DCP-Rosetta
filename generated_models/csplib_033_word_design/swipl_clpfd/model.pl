% csplib_033_word_design: a SWI-Prolog model from DCP Rosetta.
%
% Find a set of num_words words of length n over the alphabet A, C, G, T such that each word has exactly 4 symbols
% from C and G; each pair of distinct words differ in at least 4 positions; and for every pair of words x and y
% (where x and y may be identical), the reverse of x and the Watson-Crick complement of y differ in at least 4
% positions. The complement replaces each A by T, each T by A, each C by G and each G by C.
%
% Save this file as model.pl. Download `csplib_033_word_design.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_033_word_design.json')" -t halt model.pl
%
% Data fields: n (the length of each word), num_words (the number of words in the set).
% The letters are coded 1 for A, 2 for C, 3 for G and 4 for T, so the complement of letter X is 5 - X.
:- use_module(library(clpfd)).

model(Instance, Vars, [words-Words]) :-
    N = Instance.n, K = Instance.num_words,
    length(Words, K), maplist(length_is(N), Words),   % Words[I] is the I-th word
    append(Words, Letters), Letters ins 1..4,
    % each word has exactly 4 symbols from C and G
    maplist(cg_count(4), Words),
    % each pair of distinct words differ in at least 4 positions
    distinct_far(Words),
    % the reverse of x and the complement of y differ in at least 4 positions, for every pair x, y
    maplist(reverse_far(Words), Words),
    Vars = Letters.

length_is(K, L) :- length(L, K).

cg_count(K, Word) :-
    maplist(is_cg, Word, Flags),
    sum(Flags, #=, K).

is_cg(X, B) :- B #<==> (X #>= 2 #/\ X #=< 3).

distinct_far([]).
distinct_far([W|Ws]) :-
    maplist(far_apart(W), Ws),
    distinct_far(Ws).

far_apart(X, Y) :-
    maplist(differs, X, Y, Ds),
    sum(Ds, #>=, 4).

differs(A, B, D) :- D #<==> (A #\= B).

reverse_far(Words, X) :-
    reverse(X, RX),
    maplist(complement_far(RX), Words).

complement_far(RX, Y) :-
    maplist(not_complement, RX, Y, Ds),
    sum(Ds, #>=, 4).

% a letter differs from the complement of another when their codes do not add up to 5
not_complement(A, B, D) :- D #<==> (A + B #\= 5).

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
