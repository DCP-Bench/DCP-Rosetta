% building_blocks: a clingo model from DCP Rosetta.
%
% Each of a number of alphabet blocks has a single letter of the alphabet on each of its sides. In all, the blocks contain every letter but Q and Z. By arranging the blocks in various ways, you can spell all of the words in a given list, using each block for at most one letter of a word, so the letters of a word are all on different blocks. Each letter is on exactly one block, and each block has the same given number of sides. Can you figure out how the letters are arranged on the blocks?
%
% Save this file as model.lp. Download `building_blocks.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py building_blocks.json
%   python -m clingo model.lp building_blocks_1.lp

% Input: num_blocks(B) holds the number B of blocks; num_sides(S) the number S of sides of each block;
% num_letters(L) the number L of letters; alphabet(A) the letters A, and alphabet_char(P, C) the letter C at position P
% of the alphabet (indices are 0-based); words_str(I, W) the word W at position I of the list, and
% words_str_char(I, P, C) the letter C at position P of word I (indices are 0-based).

block(0..B-1) :- num_blocks(B).
letter(P, C) :- alphabet_char(P, C).

% each letter is on exactly one block
1 { dice(P, B) : block(B) } 1 :- letter(P, _).

% each block has at most as many letters as it has sides
:- num_sides(S), block(B), #count { P : dice(P, B) } > S.

% the letters of each word that are in the alphabet
in_word(I, P) :- words_str_char(I, _, C), letter(P, C).

% the distinct letters of a word are on different blocks
:- in_word(I, P1), in_word(I, P2), P1 < P2, dice(P1, B), dice(P2, B).

#show dice/2.
