(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions)

(:types row qubit - object)

(:predicates ; pauli X matrix element
             (X ?r - row ?c - qubit)
             ; pauli Z matrix element
             (Z ?r - row ?c - qubit)
             (apply_dummy)
)	

;; applying CNOT gate from qubit a to b:
;; we only change the proposition that actually change, rest are propagated implicitly:
(:action cnot
:parameters (?a ?b - qubit)
:precondition (and (not (= ?a ?b)) (not (apply_dummy)))
:effect       (and
                ;; x_b = x_a XOR x_b
                (forall(?r - row) (when (and (X ?r ?a)      (X ?r ?b))  (not (X ?r ?b))))
                (forall(?r - row) (when (and (X ?r ?a) (not (X ?r ?b)))      (X ?r ?b)))
                ;; z_a = z_a XOR z_b
                (forall(?r - row) (when (and      (Z ?r ?a)  (Z ?r ?b)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (Z ?r ?b))      (Z ?r ?a)))
                ;; apply dummy for extra weight
                (apply_dummy)
              )
)

;; dummy action for weight:
(:action dummy
:parameters ()
:precondition (and (apply_dummy))
:effect       (and (not (apply_dummy)))
)

;; Applying S gate on qubit a:
;; Similar to CNOT, we only specify the condition where the proposition flips:
(:action s-gate
:parameters (?a - qubit)
:precondition (and (not (apply_dummy)))
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
              )
)

;; Applying H gate on qubit a:
;; We only specify the condition where the proposition flips:
(:action h-gate
:parameters (?a - qubit)
:precondition (and (not (apply_dummy)))
:effect       (and
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(X ?r ?a))    (Z ?r ?a))      (and     (X ?r ?a) (not(Z ?r ?a))) ))
                (forall(?r - row) (when (and     (X ?r ?a) (not(Z ?r ?a)))     (and (not(X ?r ?a))    (Z ?r ?a))  ))
              )
)

)
