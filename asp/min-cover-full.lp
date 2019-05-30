minid(Z) :- covers(_,Z).

overlapid(X, Y) :- covers(X,Z), covers(Y,Z), X<Y.

1 { selectid(X): primeid(X) }.

covered(Z) :- selectid(X), minid(Z), covers(X,Z).
selectcount(C) :- C=#count{ X: selectid(X) }.

:- minid(Z), not covered(Z).

#minimize { C : selectcount(C) }.

#show selectid/1.
