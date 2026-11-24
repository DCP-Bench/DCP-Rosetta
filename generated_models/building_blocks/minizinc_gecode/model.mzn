% building_blocks: a MiniZinc model from DCP Rosetta.
%
% Each of a number of alphabet blocks has a single letter of the alphabet on each of its sides. In all,
% the blocks contain every letter but Q and Z. By arranging the blocks in various ways, you can spell all
% of the words in a given list, using each block for at most one letter of a word, so the letters of a
% word are all on different blocks. Each letter is on exactly one block, and each block has the same
% given number of sides. Find how the letters are arranged on the blocks.
%
% Save this file as model.mzn. Download `building_blocks.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py building_blocks.json
%   minizinc model.mzn building_blocks_1.json

include "globals.mzn";

int: num_blocks;                              % the number of blocks
int: num_sides;                               % the number of sides, and so letters, on each block
int: num_letters;                             % the number of letters in the alphabet
string: alphabet;                             % the letters of the alphabet, one character each
array[int] of string: words_str;              % the words that have to be spelled

set of int: Letters = 1..num_letters;         % one index per letter of the alphabet
set of int: Blocks = 0..num_blocks-1;         % the blocks, numbered from 0

% letters[l]: the l-th letter of the alphabet (string_split with an empty separator gives the characters)
array[int] of string: letters = string_split(alphabet, "");

% the number of a letter: its position in the alphabet
function int: letter_number(string: c) = min([l | l in Letters where letters[l] = c]);

% dice[l]: the block that letter l is on
array[Letters] of var Blocks: dice;

% the letters of each word are on different blocks
constraint forall(w in index_set(words_str))
    (alldifferent([dice[letter_number(c)] | c in string_split(words_str[w], "")]));

% each block has exactly num_sides letters on it
constraint global_cardinality(dice, [b | b in Blocks], [num_sides | b in Blocks]);

solve satisfy;
output ["{\"dice\": ", showJSON(dice), "}"];
