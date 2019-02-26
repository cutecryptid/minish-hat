#include <incmode>.

%% t = 0
#program base.
holds(m(X,A,V), 0):- m(X, A, V).
covers(X, X, 0) :- m(X, A, V).
pair(0, 1, n). pair(1, 0, n).
pair(1, 2, p). pair(2, 1, p).
pair(n, p, x). pair(p, n, x).

%% t > 0
#program step(t).
holds(m((X,Y),A,P), t) :- vadj(X,Y,A,P,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,W),t-1).
holds(m((X,Y),A,V), t) :- vadj(X,Y,_,_,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,V),t-1).

%% t >= 0
#program check(t).
id(X) :- holds(m(X,A,V),t).
adj(X,Y,t) :- id(X), id(Y), X<Y, #count{A: holds(m(X,A,V),t), holds(m(Y,A,W),t), V!=W }=1.
vadj(X,Y,A,P,t) :- adj(X,Y,t), holds(m(X,A,V),t), holds(m(Y,A,W),t), pair(V,W,P).
covers((X,Y), X, 1) :- id((X,Y)).
covers((X,Y), Y, 1) :- id((X,Y)).
covers((X,Y), Z, t) :- id((X,Y)), covers(X, Z, t-1).
covers((X,Y), Z, t) :- id((X,Y)), covers(Y, Z, t-1).
primpl(X,A,V) :- id(X), holds(m(X,A,V),t), not adj(X,_,t), not adj(_,X,t).
primplid(X) :- primpl(X,A,V).
primplcvr(X, Z) :- primplid(X), covers(X,Z,t).
primplcard(X, C) :- primplcvr(X, Z), C=#count{A: primplcvr(X, A)}.
primplequal(X, Y) :- primplcard(X, C), primplcard(Y, C), X < Y,
            #count{Z: primplcvr(X, Z), primplcvr(Y, Z)}=C.
uprimplid(X) :- primplid(X), not primplequal(X, _), not primplequal(_, X).
uprimplid(X) :- primplequal(X, _).
uprimpl(X, A, V) :- primpl(X, A, V), uprimplid(X).
uprimplcvr(X, Z) :- uprimplid(X), primplcvr(X, Z).
:- query(t), adj(X,Y,t).

#show uprimplid/1.
#show uprimpl/3.
#show uprimplcvr/2.
