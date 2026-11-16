% session3_farmer_and_cows: a SWI-Prolog model from DCP Rosetta.
%
% A farmer has cows numbered 1 up to the total number of cows, and each cow gives a quantity of milk equal to its
% number. The farmer has a number of sons and wants to give each son a given number of cows, so that the total
% quantity of milk is the same for each son. How can he distribute the cows?
%
% Save this file as model.pl. Download `session3_farmer_and_cows.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session3_farmer_and_cows.json')" -t halt model.pl
%
% Data fields: num_cows (the number of cows), num_sons (the number of sons), cows_per_son (the number of cows each
% son receives, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, [Assign, BitLists], [cow_assignments-Assign]) :-
    NumCows = Instance.num_cows,
    NumSons = Instance.num_sons,
    Counts = Instance.cows_per_son,
    Top is NumSons - 1,
    length(Assign, NumCows),
    Assign ins 0..Top,                     % the son (0-based) that each cow goes to
    % each son receives the number of cows given for him
    numlist(0, Top, Sons),
    pairs_keys_values(Pairs, Sons, Counts),
    global_cardinality(Assign, Pairs),
    % the cows are numbered 1..NumCows, and each son's cows give the same total milk (implied: the whole milk divided by the number of sons)
    numlist(1, NumCows, Cows),
    Target is NumCows * (NumCows + 1) // (2 * NumSons),
    maplist(son_milk(Assign, Cows, Target), Sons, BitLists),
    % symmetry breaking (not in the statement): sons who receive the same number of cows are interchangeable, so the first cow of the earlier son comes first
    same_count_order(Counts, BitLists).

% Bits[C] = 1 when cow C goes to Son; the milk of the son's cows is the target.
son_milk(Assign, Cows, Target, Son, Bits) :-
    maplist(in_son(Son), Assign, Bits),
    scalar_product(Cows, Bits, #=, Target).

in_son(Son, Cow, Bit) :- Bit #<==> (Cow #= Son).

same_count_order([C1, C2|Cs], [B1, B2|Bs]) :-
    (   C1 =:= C2 -> precedes(B1, B2) ; true ),
    same_count_order([C2|Cs], [B2|Bs]).
same_count_order([_], [_]).

% Seen is 1 once a cow of the earlier son has been passed; a cow of the later son needs one before it.
precedes(EarlierBits, LaterBits) :-
    Seen #= 0,
    precedes(EarlierBits, LaterBits, Seen).

precedes([], [], _).
precedes([E|Es], [L|Ls], Seen) :-
    L #==> Seen,
    Seen1 #<==> (Seen #\/ E),
    precedes(Es, Ls, Seen1).

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
