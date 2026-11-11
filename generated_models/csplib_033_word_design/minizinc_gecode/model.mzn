% csplib_033_word_design: a MiniZinc model from DCP Rosetta.
%
% Find a set S of num_words strings (words) of length n over the alphabet W = {A, C, G, T} with the following properties:
%
% - Each word in S has 4 symbols from {C, G};
% - Each pair of distinct words in S differ in at least 4 positions; and
% - Each pair of words x and y in S (where x and y may be identical) are such that x^R and y^C differ in at least 4
%   positions. For example, when n=8, (x_1,...,x_8)^R = (x_8,...,x_1) is the reverse of (x_1,...,x_8) and
%   (y_1,...,y_8)^C is the Watson-Crick complement of (y_1,...,y_8), i.e. the word where each A is replaced by a T and
%   vice versa and each C is replaced by a G and vice versa.
%
% Save this file as model.mzn. Download `csplib_033_word_design.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_033_word_design.json
%   minizinc model.mzn csplib_033_word_design_1.json

int: n;                                           % the length of each word
int: num_words;                                   % the number of words in the set

set of int: Positions = 1..n;                     % the positions of a word
set of int: Words = 1..num_words;                 % the words of the set
% the letters A, C, G and T, numbered 1, 2, 3 and 4
set of int: Letters = 1..4;
set of int: CG = 2..3;                            % the letters C and G
% the Watson-Crick complement of letter a is 5 - a: A and T swap, C and G swap
int: MinDifference = 4;                           % the words differ in at least this many positions

% words[i,p]: the letter at position p of word i
array[Words, Positions] of var Letters: words;

% each word has 4 symbols from {C, G}
constraint forall(i in Words)(sum(p in Positions)(bool2int(words[i, p] in CG)) = 4);

% each pair of distinct words differ in at least 4 positions
constraint forall(i in Words, j in Words where i < j)(
    sum(p in Positions)(bool2int(words[i, p] != words[j, p])) >= MinDifference);

% the reverse of each word and the complement of each word differ in at least 4 positions, for every pair of words
constraint forall(i in Words, j in Words)(
    sum(p in Positions)(bool2int(words[i, n + 1 - p] != 5 - words[j, p])) >= MinDifference);

solve satisfy;

output ["{\"words\": ", showJSON(words), "}"];
