% crossword: a MiniZinc model from DCP Rosetta.
%
% We are to complete a crossword puzzle on a grid of 6 rows and 5 columns, with 8 blocked squares and
% the numbers 1 to 8 marking where the words start: 1 across and down from the top left, and so on.
% Given the list of 15 words AFT, ALE, EEL, HEEL, HIKE, HOSES, KEEL, KNOT, LASER, LEE, LINE, SAILS,
% SHEET, STEER and TIE, select 8 words from the list such that the crossword puzzle can be completed:
% each word fills the slot that starts at its number, and crossing words agree on their shared letter.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

set of int: Words = 0..14;                  % the 15 words, sorted by length (longest first), then alphabetically

% word_letters[w, k]: the k-th letter of word w (A = 1, ..., Z = 26), 0 past the last letter
array[Words, 1..5] of 0..26: word_letters = array2d(Words, 1..5, [
    8, 15, 19,  5, 19,    % HOSES
   12,  1, 19,  5, 18,    % LASER
   19,  1,  9, 12, 19,    % SAILS
   19,  8,  5,  5, 20,    % SHEET
   19, 20,  5,  5, 18,    % STEER
    8,  5,  5, 12,  0,    % HEEL
    8,  9, 11,  5,  0,    % HIKE
   11,  5,  5, 12,  0,    % KEEL
   11, 14, 15, 20,  0,    % KNOT
   12,  9, 14,  5,  0,    % LINE
    1,  6, 20,  0,  0,    % AFT
    1, 12,  5,  0,  0,    % ALE
    5,  5, 12,  0,  0,    % EEL
   12,  5,  5,  0,  0,    % LEE
   20,  9,  5,  0,  0]);  % TIE
% word_len[w]: the number of letters in word w
array[Words] of int: word_len = array1d(Words, [5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3]);

% open_cell[r, c]: the square in row r and column c is not blocked
array[1..6, 1..5] of bool: open_cell = array2d(1..6, 1..5, [
    true,  true,  true,  true,  true,
    false, false, true,  false, true,
    false, true,  true,  true,  true,
    true,  false, true,  true,  true,
    true,  true,  true,  true,  true,
    true,  false, false, true,  false]);

% E[i]: the word that starts at number i
array[1..8] of var Words: E;

% L[r, c]: the letter in the square in row r and column c (A = 1, ..., Z = 26), 0 for a blocked square
array[1..6, 1..5] of var 0..26: L;

% a blocked square holds no letter, an open square holds one
constraint forall(r in 1..6, c in 1..5)(L[r, c] = 0 <-> not open_cell[r, c]);

% the 8 words are different
constraint all_different(E);

% the word w fills the squares of cells, one letter each: its length is the number of cells and its
% letters are those of the cells
predicate spells(var Words: w, array[int] of var 0..26: cells) =
    word_len[w] = card(index_set(cells)) /\
    forall(k in index_set(cells))(word_letters[w, k] = cells[k]);

% the word starting at number 1 runs across the top row
constraint spells(E[1], [L[1, c] | c in 1..5]);
% the word starting at number 2 runs down column 3
constraint spells(E[2], [L[r, 3] | r in 1..5]);
% the word starting at number 3 runs down column 5
constraint spells(E[3], [L[r, 5] | r in 1..5]);
% the word starting at number 4 runs across row 3
constraint spells(E[4], [L[3, c] | c in 2..5]);
% the word starting at number 5 runs down column 4
constraint spells(E[5], [L[r, 4] | r in 3..6]);
% the word starting at number 6 runs down column 1
constraint spells(E[6], [L[r, 1] | r in 4..6]);
% the word starting at number 7 runs across row 4
constraint spells(E[7], [L[4, c] | c in 3..5]);
% the word starting at number 8 runs across row 5
constraint spells(E[8], [L[5, c] | c in 1..5]);

solve satisfy;

output ["{\"E\": ", showJSON(E), "}"];
