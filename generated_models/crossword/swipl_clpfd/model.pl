% crossword: a SWI-Prolog model from DCP Rosetta.
%
% Complete the crossword grid (5 columns, 6 rows, numbered slots 1 to 8) by selecting 8 words from the list of 15
% words: AFT, ALE, EEL, HEEL, HIKE, HOSES, KEEL, KNOT, LASER, LEE, LINE, SAILS, SHEET, STEER and TIE. The 8 words
% must be different, each must fill its slot, and the words that cross must agree on the letter they share.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl

:- use_module(library(clpfd)).

% The 15 words, numbered from 0 in the order longest first, then alphabetically.
words(['HOSES', 'LASER', 'SAILS', 'SHEET', 'STEER',
       'HEEL', 'HIKE', 'KEEL', 'KNOT', 'LINE',
       'AFT', 'ALE', 'EEL', 'LEE', 'TIE']).

% Every word is padded with 0 to this many cells (the length of the longest word).
cell_width(5).

% Slots 1 to 8 are numbered as in the grid; slot S (from 0) is the one numbered S+1:
%   slot 0: 1 across, 5 cells;  slot 1: 2 down, 5 cells;  slot 2: 3 down, 5 cells;
%   slot 3: 4 across, 4 cells;  slot 4: 5 down, 4 cells;  slot 5: 6 down, 3 cells;
%   slot 6: 7 across, 3 cells;  slot 7: 8 across, 5 cells.
slot_lengths([5, 5, 5, 4, 4, 3, 3, 5]).

% Each entry [SlotA, PosA, SlotB, PosB] is a cell where slot SlotA at position PosA (from 1) crosses slot SlotB at
% position PosB: the two letters there must be equal.
crossings([[0, 3, 1, 1], [0, 5, 2, 1], [3, 2, 1, 3], [3, 3, 4, 1], [3, 4, 2, 3], [6, 1, 1, 4],
           [6, 2, 4, 2], [6, 3, 2, 4], [7, 1, 5, 2], [7, 3, 1, 5], [7, 4, 4, 3], [7, 5, 2, 5]]).

model(_Instance, E, ['E'-E]) :-
    words(Words),
    length(Words, NumWords),
    Last is NumWords - 1,
    maplist(atom_length, Words, WordLengths),
    slot_lengths(SlotLengths),
    % E[S] is the word, by number, that fills slot S
    length(SlotLengths, NumSlots),
    length(E, NumSlots),
    E ins 0..Last,
    % the 8 words are different
    all_distinct(E),
    % each word fills a slot of its own length
    maplist(fits_slot(WordLengths), E, SlotLengths),
    % the letters of all words as numbers (A=1 .. Z=26), each word padded with 0 to cell_width cells: word W, cell P is at Width*W+P
    maplist(word_cells, Words, Rows),
    append(Rows, Cells),
    % where two slots cross, the two words show the same letter
    crossings(Crossings),
    maplist(crossing_agrees(E, Cells), Crossings).

fits_slot(WordLengths, Word, Length) :-
    Index #= Word + 1,
    element(Index, WordLengths, Length).

word_cells(Word, Cells) :-
    atom_codes(Word, Codes),
    maplist(letter_number, Codes, Letters),
    length(Letters, Len),
    cell_width(Width),
    Pad is Width - Len,
    length(Zeros, Pad),
    maplist(=(0), Zeros),
    append(Letters, Zeros, Cells).

letter_number(Code, Number) :-
    Number is Code - 64.

crossing_agrees(E, Cells, [SlotA, PosA, SlotB, PosB]) :-
    letter(E, Cells, SlotA, PosA, LetterA),
    letter(E, Cells, SlotB, PosB, LetterB),
    LetterA #= LetterB.

letter(E, Cells, Slot, Pos, Letter) :-
    nth0(Slot, E, Word),
    cell_width(Width),
    Index #= Width * Word + Pos,
    element(Index, Cells, Letter).

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
