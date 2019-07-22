dstphead((P2,R2),(P1,R1),A) :- rule(P2,R2), rule(P1,R1), phead(P2,R2,A), not phead(P1,R1,A),
                                P1 < P2.
dstnhead((P2,R2),(P1,R1),A) :- rule(P2,R2), rule(P1,R1), nhead(P2,R2,A), not nhead(P1,R1,A),
                                P1 < P2.
dstpbody((P2,R2),(P1,R1),A) :- rule(P2,R2), rule(P1,R1), pbody(P2,R2,A), not pbody(P1,R1,A),
                              P1 < P2.
dstnbody((P2,R2),(P1,R1),A) :- rule(P2,R2), rule(P1,R1), nbody(P2,R2,A), not nbody(P1,R1,A),
                              P1 < P2.

dstrules((P2,R2),(P1,R1)) :- rule(P2,R2), rule(P1,R1), P1 < P2, dstphead((P2,R2),(P1,R1),_).
dstrules((P2,R2),(P1,R1)) :- rule(P2,R2), rule(P1,R1), P1 < P2, dstnhead((P2,R2),(P1,R1),_).
dstrules((P2,R2),(P1,R1)) :- rule(P2,R2), rule(P1,R1), P1 < P2, dstpbody((P2,R2),(P1,R1),_).
dstrules((P2,R2),(P1,R1)) :- rule(P2,R2), rule(P1,R1), P1 < P2, dstnbody((P2,R2),(P1,R1),_).

cntrules(P2,R2,P1,R1) :- rule(P2,R2), rule(P1,R1), P1 < P2, not dstrules((P2,R2),(P1,R1)).

notsuper(P2,R2) :- rule(P2,R2), rule(P1,R1), P1 < P2, not cntrules(P2,R2,_,_).

#show cntrules/4.
#show notsuper/2.
