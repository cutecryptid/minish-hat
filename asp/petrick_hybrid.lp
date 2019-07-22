overlapid(X, Y) :- covers(X,Z), covers(Y,Z), X<Y.

minid(Z) :- covers(_,Z).

1 { selectid(X): leftid(X) }.

selectidcovers(X, Z) :- selectid(X), covers(X, Z).
selectminid(Z) :- selectidcovers(_,Z).

:- minid(Z), not selectminid(Z).
:- selectid(X), selectid(Y), X<Y, overlapid(X,Y).

#show selectid/1.
