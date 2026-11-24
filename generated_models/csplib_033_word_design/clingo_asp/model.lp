% csplib_033_word_design: a clingo model from DCP Rosetta.
%
% Find a set S of num_words strings (words) of length n over the alphabet {A,C,G,T} with the following properties: each word in S has 4 symbols from {C,G}; each pair of distinct words in S differ in at least 4 positions; and each pair of words x and y in S (where x and y may be identical) are such that the reverse of x and the Watson-Crick complement of y differ in at least 4 positions. The Watson-Crick complement replaces each A by a T and vice versa, and each C by a G and vice versa.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
% Save this file as model.lp. Download `csplib_033_word_design.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_033_word_design.json
%   python -m clingo model.lp csplib_033_word_design_1.lp

% Input: n(N): the length N of each word; num_words(M): the number M of words. The words are numbered
% 0..M-1 and the positions 0..N-1 (indices are 0-based). The letters are 1 for A, 2 for C, 3 for G and 4 for T,
% so the complement of letter L is 5-L.

word(0..M-1) :- num_words(M).
pos(0..N-1) :- n(N).
letter(1..4).

% words(W,P,L): word W has letter L at position P; each position holds exactly one letter
1 { words(W,P,L) : letter(L) } 1 :- word(W), pos(P).

% each word has exactly 4 symbols from {C, G}
:- word(W), #count { P,c : words(W,P,2) ; P,g : words(W,P,3) } != 4.

% each pair of distinct words differ in at least 4 positions, so they agree in at most n-4 positions
:- word(W1), word(W2), W1 < W2, n(N), #count { P : words(W1,P,L), words(W2,P,L) } > N-4.

% for each pair of words x and y, possibly the same, the reverse of x and the complement of y differ in
% at least 4 positions: position P of the reverse of x is letter N-1-P of x, and the complement of y at P is 5-L
:- word(W1), word(W2), n(N), #count { P : words(W1,N-1-P,L), words(W2,P,5-L) } > N-4.

#show words/3.
