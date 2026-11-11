% de_bruijn_sequence: a MiniZinc model from DCP Rosetta.
%
% A de Bruijn sequence of order n on an alphabet of base symbols is a cyclic sequence in which every
% possible length-n string on the alphabet occurs exactly once as a substring. Such a sequence has length
% base^n.
%
% Save this file as model.mzn. Download `de_bruijn_sequence.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py de_bruijn_sequence.json
%   minizinc model.mzn de_bruijn_sequence_1.json

include "globals.mzn";

int: base;                                       % the size of the alphabet
int: n;                                          % the order: the length of the substrings

set of int: Symbols = 0..base-1;                 % the symbols of the alphabet
int: seq_len = pow(base, n);                     % the length of the sequence
set of int: Pos = 1..seq_len;                    % the positions of the sequence (cyclic)
set of int: Digits = 0..n-1;                     % the offsets within a substring

% de_bruijn[p]: the symbol at position p
array[Pos] of var Symbols: de_bruijn;

% code[p]: the substring of length n starting at position p, read as a base-base number
array[Pos] of var 0..seq_len-1: code;

% code[p] is the substring of length n starting at position p, wrapping around the cyclic sequence
constraint forall(p in Pos)(
    code[p] = sum(j in Digits)(pow(base, j) * de_bruijn[(p + j - 1) mod seq_len + 1])
);

% every length-n string occurs exactly once as a substring
constraint all_different(code);

solve satisfy;
output ["{\"de_bruijn\": ", showJSON(de_bruijn), "}"];
