% handshaking: a clingo model from DCP Rosetta.
%
% Hilary and Jocelyn are married. They invite a number of couples who are friends for dinner. When they
% arrive, they shake hands with each other. Nobody shakes hands with him or herself or with his or her
% spouse. After there has been some handshaking, Jocelyn jumps up on a chair and says 'Stop shaking hands!',
% and then asks how many hands each person has shaken. All the answers are different. Find the number of
% hands Hilary has shaken.
%
% Save this file as model.lp. Download `handshaking.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py handshaking.json
%   python -m clingo model.lp handshaking_1.lp
%
% Input: num_couples(C) holds the number C of couples invited, not counting Hilary and Jocelyn.
% The people are numbered 0 to 2C+1: Hilary is 0, Jocelyn is 1, and the spouses of the invited couples
% are 2K and 2K+1 for K = 1 to C.

person(0..2 * C + 1) :- num_couples(C).

% spouse(I, J): person I and person J are married to each other
spouse(I, I + 1) :- person(I), I \ 2 = 0.
spouse(J, I) :- spouse(I, J).

% shake(I, J): persons I and J shake hands; a handshake is listed once, with I < J, and it is between two
% people who are not married to each other
{ shake(I, J) : person(I), person(J), I < J, not spouse(I, J) }.

% hand(I, J): person I and person J have shaken hands, in either direction
hand(I, J) :- shake(I, J).
hand(J, I) :- shake(I, J).

% hands(I, D): person I has shaken D hands
hands(I, D) :- person(I), D = #count { J : hand(I, J) }.

% Jocelyn asks everyone except herself, so the answers are those of Hilary and the guests
answer(I, D) :- hands(I, D), person(I), I != 1.

% all the answers are different
:- answer(I, D), answer(J, D), I < J.

% symmetry breaking: the guests can be renamed without changing any answer, so each guest couple has its
% even-numbered person with at least as many hands as the odd-numbered one, and the couples are listed by
% decreasing number of hands of their even-numbered person
:- hands(I, D), hands(I + 1, E), I >= 2, I \ 2 = 0, D < E.
:- hands(I, D), hands(I + 2, E), I >= 2, I \ 2 = 0, D < E.

% hil(D): Hilary has shaken D hands
hil(D) :- hands(0, D).

% the handshakes themselves are not part of the answer, so the solutions are projected onto hil
#project hil/1.
#show hil/1.
