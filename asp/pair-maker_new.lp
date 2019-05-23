#include <incmode>.
symbol(0;1;2;z;o;x).

pair(0, 1, z).
pair(1, 2, o).
pair(z, o, x).

pair(Y, X, Z) :- pair(X, Y, Z).
partial(X, Y, X) :- pair(_,X,Y).
partial(Y, X, X) :- partial(X, Y, X).

belongs(X, Y) :- pair(X,_,Y).
belongs(X, Y) :- pair(_,X,Y).
belongs(0, x). belongs(1, x). belongs(2, x).

unbelongs(X,Y) :- symbol(X), symbol(Y), X!=Y, not belongs(X,Y).

%% t = 0
#program base.
holds(m(X,A,V), 0):- m(X, A, V).
covers(X, X, 0) :- m(X, A, V).

%% t > 0
#program step(t).
holds(m((X,Y),A,P), t) :- adj(X,Y,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,W),t-1), pair(V, W, P).
holds(m((X,Y),A,Z), t) :- adj(X,Y,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,W),t-1), partial(V, W, Z).
holds(m((X,Y),A,V), t) :- adj(X,Y,t-1), holds(m(X,A,V),t-1), holds(m(Y,A,V),t-1).
holds(m(X,A,V), t) :- subsum(X,Y,t-1), holds(m(X,A,V),t-1).

%%TODO: Rethink usedatomvalue
%%TODO: Rethink mark, depends only on original algorithm or also usedatomvalue?
usedatomvalue(X, A, V, t) :- holds(m((X,Y),A,P), t), holds(m(X,A,V),t-1), pair(V,_,P).
usedatomvalue(Y, A, W, t) :- holds(m((X,Y),A,P), t), holds(m(Y,A,W),t-1), pair(_,W,P).

%% t >= 0
#program check(t).
id(X, t) :- holds(m(X,A,V),t).
id(X) :- id(X, t).

subsum(X,Y,t) :- id(X,t), id(Y,t), X!=Y,
                #count{A: holds(m(X,A,V),t), holds(m(Y,A,W),t), pair(V,W,_)}=0,
                #count{A: holds(m(X,A,V),t), holds(m(Y,A,W),t), unbelongs(W,V)}=0.

adj(X,Y,t) :- id(X,t), id(Y,t), X!=Y,
              #count{A: holds(m(X,A,V),t), holds(m(Y,A,W),t), pair(V, W,_)}=1,
              #count{A: holds(m(X,A,V),t), holds(m(Y,A,W),t), unbelongs(V,W), not pair(V, W,_) }=0.

adj(X,Y,A,P,t) :- adj(X,Y,t), holds(m(X,A,V),t), holds(m(Y,A,W),t), pair(V,W,P).

%%TODO: Rethink covers based on mark/unmark

:- query(t), adj(X,Y,t).
:- query(t), subsum(X,Y,t).

#show adj/3.
