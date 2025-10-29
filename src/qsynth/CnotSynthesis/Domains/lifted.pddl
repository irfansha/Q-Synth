
(define (domain Cnot-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions)

(:types row qubit - object)

(:predicates (X ?r ?c - qubit))

; only the matrix elements that change based on XOR operation are added
; unchanged cases are propogated directly:

(:action cnot
:parameters (?c ?t - qubit)
:precondition (and (not (= ?c ?t)))
:effect       (and 
                (forall(?r - qubit) (when (and (X ?r ?c)      (X ?r ?t)) (not (X ?r ?t))))
                (forall(?r - qubit) (when (and (X ?r ?c) (not (X ?r ?t)))     (X ?r ?t)))
              )
)
)
