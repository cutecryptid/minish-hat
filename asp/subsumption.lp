phd(X, A) :- m(X,A,z).
phd(X, A) :- m(X,A,1).
nhd(X, A) :- m(X,A,o).
nhd(X, A) :- m(X,A,1).
pbd(X, A) :- m(X,A,2).
nbd(X, A) :- m(X,A,0).

#show phd/2.
#show nhd/2.
#show pbd/2.
#show nbd/2.
