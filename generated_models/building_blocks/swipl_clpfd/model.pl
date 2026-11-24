% building_blocks: a SWI-Prolog model from DCP Rosetta.
%
% Each of a number of alphabet blocks has one letter of the alphabet on each of its sides. Together the blocks carry
% every letter except Q and Z, each letter on exactly one block, and every block has the same number of sides. Arrange
% the letters on the blocks so that every word of the given list can be spelled: each block is used for at most one
% letter of a word, so the letters of a word all lie on different blocks.
%
% Save this file as model.pl. Download `building_blocks.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('building_blocks.json')" -t halt model.pl
%
% Data fields: alphabet (the letters, in order, as one string), num_blocks (the number of blocks), num_letters (the
% number of letters), num_sides (the number of sides of each block), words_str (the words to spell, as strings).
:- use_module(library(clpfd)).

model(Instance, Vars, [dice-Dice]) :-
    NumBlocks = Instance.num_blocks,
    NumSides = Instance.num_sides,
    NumLetters = Instance.num_letters,
    atom_chars(Instance.alphabet, Letters),
    Words = Instance.words_str,
    Last is NumBlocks - 1,
    % Dice[L]: the block carrying the letter number L of the alphabet, counted from 0
    length(Dice, NumLetters),
    Dice ins 0..Last,
    % each block carries exactly num_sides letters
    findall(B-NumSides, between(0, Last, B), Counts),
    global_cardinality(Dice, Counts),
    % the letters of each word lie on different blocks
    maplist(word_on_different_blocks(Letters, Dice), Words),
    Vars = Dice.

% The letters of Word are on pairwise different blocks.
word_on_different_blocks(Letters, Dice, Word) :-
    atom_chars(Word, WordLetters),
    maplist(block_of_letter(Letters, Dice), WordLetters, Blocks),
    all_distinct(Blocks).

% Block is the block carrying Letter.
block_of_letter(Letters, Dice, Letter, Block) :-
    once(nth0(I, Letters, Letter)),
    nth0(I, Dice, Block).

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
