% Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
% pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
% cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.
:- lib(ic).

% The instance has no fields: every number below is from the problem statement.
model(_Instance, [T, H, R, S, N], [t-T, h-H, r-R, s-S, n-N], min(Cost)) :-
    % T: he wears a green tie, H: a green hat, R: a green shirt, S: green socks,
    % N: he pays the entrance fee (each 1 for yes, 0 for no)
    [T, H, R, S, N] #:: 0..1,

    % Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    % rule holds or he pays.
    % Rule 1: if someone wears a green tie he has to wear a green shirt.
    ((T #= 1 => R #= 1) or N #= 1),
    % Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    % a green hat.
    (((S #= 1 or R #= 1) => (T #= 1 or H #= 1)) or N #= 1),
    % Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    % must wear a green tie.
    (((R #= 1 or H #= 1 or S #= 0) => T #= 1) or N #= 1),

    % Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    Cost = 10 * T + 2 * H + 12 * S + 11 * N.
