(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions :action-costs)

(:types row qubit - object)

(:predicates ; pauli X matrix element
             (X ?r - row ?c - qubit)
             ; pauli Z matrix element
             (Z ?r - row ?c - qubit)
             ; indicates whether single qubit gate has been applied on qubit a
             ; we disable further single qubit gates on qubit a after one has been applied
             (applied_1q ?a)
             ; qubits ?a and ?b are connected;
             ; static predicate
             (connected ?a ?b - qubit)
)

(:functions
  (total-cost) - number
  (cnot-cost) - number
)

;; applying CNOT gate from qubit a to b:
;; we only change the proposition that actually change, rest are propagated implicitly:
(:action cnot
:parameters (?a ?b - qubit)
:precondition (and (not (= ?a ?b)) (connected ?a ?b))
:effect       (and
                ;; x_b = x_a XOR x_b
                (forall(?r - row) (when (and (X ?r ?a)      (X ?r ?b))  (not (X ?r ?b))))
                (forall(?r - row) (when (and (X ?r ?a) (not (X ?r ?b)))      (X ?r ?b)))
                ;; z_a = z_a XOR z_b
                (forall(?r - row) (when (and      (Z ?r ?a)  (Z ?r ?b)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (Z ?r ?b))      (Z ?r ?a)))
                ;; allow single qubit gates on both qubits after CNOT:
                (not (applied_1q ?a))
                (not (applied_1q ?b))
                (increase (total-cost) (cnot-cost))
              )
)

;; Applying S gate on qubit a:
;; Similar to CNOT, we only specify the condition where the proposition flips:
(:action s-gate
:parameters (?a - qubit)
:precondition (and (not (applied_1q ?a)))
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
                (applied_1q ?a)
                (increase (total-cost) 1)
              )
)

;; Applying H gate on qubit a:
;; We only specify the condition where the proposition flips:
(:action h-gate
:parameters (?a - qubit)
:precondition (and (not (applied_1q ?a)))
:effect       (and
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(X ?r ?a))    (Z ?r ?a))      (and     (X ?r ?a) (not(Z ?r ?a))) ))
                (forall(?r - row) (when (and     (X ?r ?a) (not(Z ?r ?a)))     (and (not(X ?r ?a))    (Z ?r ?a))  ))
                (applied_1q ?a)
                (increase (total-cost) 1)
              )
)

;; Applying HS gate on qubit a:
(:action hs-gate
:parameters (?a - qubit)
:precondition (and (not (applied_1q ?a)))
:effect       (and
                ;; x_a = z_a
                (forall(?r - row) (when (and      (Z ?r ?a))       (X ?r ?a)))
                (forall(?r - row) (when (and (not (Z ?r ?a))) (not (X ?r ?a))))
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
                (applied_1q ?a)
                (increase (total-cost) 2)
              )
)

;; Applying SH gate on qubit a:
(:action sh-gate
:parameters (?a - qubit)
:precondition (and (not (applied_1q ?a)))
:effect       (and
                ;; x_a = x_a + z_a
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                ;; z_a = x_a
                (forall(?r - row) (when (and      (X ?r ?a))       (Z ?r ?a)))
                (forall(?r - row) (when (and (not (X ?r ?a))) (not (Z ?r ?a))))
                (applied_1q ?a)
                (increase (total-cost) 2)
              )
)

;; Applying Sx gate on qubit a:
;; =============
;; -------------
;; Sx = S H S
;; -------------
;; =============
;; we only specify the condition where the proposition flips:
(:action sx-gate
:parameters (?a - qubit)
:precondition (and (not (applied_1q ?a)))
:effect       (and
                ;; x_a = z_a XOR x_a
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                (applied_1q ?a)
                (increase (total-cost) 1)
              )
)

)
