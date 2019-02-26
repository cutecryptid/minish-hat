overlapid(X, Y) :- leftimplcvr(X,Z), leftimplcvr(Y,Z), X<Y.

1{ selectimplid(X):leftimplid(X) }.

selectimplcvr(X, Z) :- selectimplid(X), leftimplcvr(X, Z).
selectimpl(X, A, V) :- selectimplid(X), leftimpl(X, A, V).

fullcover :- C=#count{X:leftimplid(X)}, D=#count{Z:selectimplcvr(_,Z)}, C=D.

:- selectimplid(X), selectimplid(Y), X<Y, overlapid(X,Y).
:- not fullcover.

#show selectimplid/1.
#show selectimplcvr/2.
#show selectimpl/3.
#show fullcover/0.
