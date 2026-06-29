(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions)

(:types row qubit - object)

(:predicates
            (X ?r - row ?c - qubit)            ; pauli X matrix element
            (Z ?r - row ?c - qubit)            ; pauli Z matrix element
            (disabled ?a - qubit)              ; disable qubit after last gate:
            (applied_1q ?a - qubit)   ; to indicate single qubit gate has been applied:
            (connected ?a ?b - qubit)          ; qubits ?a and ?b are connected (static); also a < b for normal form
)

;; Applying I gate on qubit i:
(:action i-gate
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and (applied_1q ?a))
)

;; Applying HS gate on qubit i:
(:action hs-gate
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (applied_1q ?a)
                ;; x_i = z_i
                (forall(?r - row) (when (and      (Z ?r ?a))       (X ?r ?a)))
                (forall(?r - row) (when (and (not (Z ?r ?a))) (not (X ?r ?a))))
                ;; z_i = z_i XOR x_i
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
              )
)

;; Applying SH gate on qubit i:
(:action sh-gate
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (applied_1q ?a)
                ;; x_i = x_i + z_i
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                ;; z_i = x_i
                (forall(?r - row) (when (and      (X ?r ?a))       (Z ?r ?a)))
                (forall(?r - row) (when (and (not (X ?r ?a))) (not (Z ?r ?a))))
              )
)

;; applying CNOT gate from qubit i to j:
;; we only change the proposition that actually change, rest are propagated implicitly:
(:action cnot
:parameters (?a ?b - qubit)
:precondition (and (connected ?a ?b)
                   (not (disabled ?a)) (not (disabled ?b))
                   (applied_1q ?a) (applied_1q ?b)
              )
:effect       (and
                (not (applied_1q ?a)) (not (applied_1q ?b))
                ;; x_j = x_i XOR x_j
                (forall(?r - row) (when (and (X ?r ?a)      (X ?r ?b))  (not (X ?r ?b))))
                (forall(?r - row) (when (and (X ?r ?a) (not (X ?r ?b)))      (X ?r ?b)))
                ;; z_i = z_i XOR z_j
                (forall(?r - row) (when (and      (Z ?r ?a)  (Z ?r ?b)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (Z ?r ?b))      (Z ?r ?a)))
              )
)

;; ==================================================================
;; Layer single qubit gates layer actions:
;; apply a gate and disable that qubit:
;; ==================================================================

;; Applying I gate on qubit i:
(:action i-gate-last
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and (disabled ?a))
)

;; Applying HS gate on qubit i:
(:action hs-gate-last
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (disabled ?a)
                ;; x_i = z_i
                (forall(?r - row) (when (and      (Z ?r ?a))       (X ?r ?a)))
                (forall(?r - row) (when (and (not (Z ?r ?a))) (not (X ?r ?a))))
                ;; z_i = z_i XOR x_i
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
              )
)

;; Applying SH gate on qubit i:
(:action sh-gate-last
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (disabled ?a)
                ;; x_i = x_i + z_i
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                ;; z_i = x_i
                (forall(?r - row) (when (and      (X ?r ?a))       (Z ?r ?a)))
                (forall(?r - row) (when (and (not (X ?r ?a))) (not (Z ?r ?a))))
              )
)

;; Applying S gate:
(:action s-gate-last
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (disabled ?a)
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
              )
)

;; Applying H gate on qubit a:
;; We only specify the condition where the proposition flips:
(:action h-gate-last
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (disabled ?a)
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(X ?r ?a))    (Z ?r ?a))      (and     (X ?r ?a) (not(Z ?r ?a))) ))
                (forall(?r - row) (when (and     (X ?r ?a) (not(Z ?r ?a)))     (and (not(X ?r ?a))    (Z ?r ?a))  ))
              )
)

;; Applying HSH gate, i.e., sx-gate on qubit i:
(:action sx-gate-last
:parameters (?a - qubit)
:precondition (and (not (disabled ?a)) (not (applied_1q ?a)))
:effect       (and
                (disabled ?a)
                ;; x_i = x_i + z_i
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
              )
)

)
