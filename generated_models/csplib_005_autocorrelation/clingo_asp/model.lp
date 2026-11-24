% csplib_005_autocorrelation: a clingo model from DCP Rosetta.
%
% These problems have many practical applications in communications and electrical engineering. The objective is to
% construct a binary sequence of length n that minimizes the autocorrelations between bits. Each bit in the sequence
% takes the value +1 or -1. With periodic (or cyclic) boundary conditions, the k-th autocorrelation, C_k, is defined
% to be the sum over i from 0 to n-1 of S_i * S_((i+k) mod n). This problem uses the periodic ones: the aim is to
% minimize the sum of their squares, that is, to minimize E = the sum over k from 1 to n-1 of C_k^2.
%
% Save this file as model.lp. Download `csplib_005_autocorrelation.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_005_autocorrelation.json
%   python -m clingo model.lp csplib_005_autocorrelation_1.lp
%
% Input: n(N) holds the length N of the sequence (the bits are numbered 0 to N-1).

% sign(I, V): bit I of the sequence has the value V, which is +1 or -1
{ sign(I,1) } :- n(N), I = 0..N-1.
sign(I,-1) :- n(N), I = 0..N-1, not sign(I,1).

% autocorr(K, V): the K-th periodic autocorrelation of the sequence is V, the sum over all bits I of the
% product of bit I and bit (I+K) mod N
autocorr(K,V) :- n(N), K = 1..N-1,
                 V = #sum { X*Y,I : sign(I,X), J = (I+K)\N, sign(J,Y) }.

% the energy, the sum of the squares of the autocorrelations, is as small as possible
#minimize { V*V,K : autocorr(K,V) }.

% sequence(I, V): bit I of the sequence has the value V
sequence(I,V) :- sign(I,V).

#show sequence/2.
