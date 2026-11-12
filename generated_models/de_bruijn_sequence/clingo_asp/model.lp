% de_bruijn_sequence: a clingo model from DCP Rosetta.
%
% In combinatorial mathematics, a de Bruijn sequence of order n on an alphabet of base symbols is a cyclic
% sequence of base^n symbols in which every possible length-n string on the alphabet occurs exactly once as a
% substring. Find such a sequence.
%
% Save this file as model.lp. Download `de_bruijn_sequence.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py de_bruijn_sequence.json
%   python -m clingo model.lp de_bruijn_sequence_1.lp

% Input: base(B): the size B of the alphabet, with symbols 0..B-1; n(N): the order N.

size(B**N) :- base(B), n(N).
pos(0..B**N-1) :- base(B), n(N).
place(0..N-1) :- n(N).
symbol(0..B-1) :- base(B).

% each position of the cycle holds exactly one symbol
1 { symbol_at(P,V) : symbol(V) } 1 :- pos(P).

% window(P, X): the length-n string starting at position P, read cyclically, as the number X in base B
window(P,X) :- pos(P), base(B), n(N), size(L),
               X = #sum { V*B**(N-1-J),J : place(J), symbol_at((P+J) \ L,V) }.

% every length-n string occurs exactly once: the windows read different numbers
:- window(P1,X), window(P2,X), P1 < P2.

% the sequence is the list of symbols around the cycle
de_bruijn(P,V) :- symbol_at(P,V).

#show de_bruijn/2.
