(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions)

(:types row qubit - object)

(:predicates ;; intermediate matrix elements:
             ; pauli X matrix element
             (IX ?r - row ?q - qubit)
             ; pauli Z matrix element
             (IZ ?r - row ?q - qubit)
             ;; main matrix elements for goal and after permutation
             ; pauli X matrix element
             (X ?r - row ?q - qubit)
             ; pauli Z matrix element
             (Z ?r - row ?q - qubit)
             (permuted )
             ;; keeping track of final mapping:
             (imapped ?q - qubit)
             (mapped ?q - qubit)
)

;; applying CNOT gate from qubit a to b:
;; we only change the proposition that actually change, rest are propagated implicitly:
(:action cnot
:parameters (?a ?b - qubit)
:precondition (and (not (= ?a ?b)) (not (permuted )))
:effect       (and
                ;; x_b = x_a XOR x_b
                (forall(?r - row) (when (and (IX ?r ?a)      (IX ?r ?b))  (not (IX ?r ?b))))
                (forall(?r - row) (when (and (IX ?r ?a) (not (IX ?r ?b)))      (IX ?r ?b)))
                ;; z_a = z_a XOR z_b
                (forall(?r - row) (when (and      (IZ ?r ?a)  (IZ ?r ?b)) (not (IZ ?r ?a))))
                (forall(?r - row) (when (and (not (IZ ?r ?a)) (IZ ?r ?b))      (IZ ?r ?a)))
              )
)

;; Applying S gate on qubit a:
;; Similar to CNOT, we only specify the condition where the proposition flips:
(:action s-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (IZ ?r ?a)  (IX ?r ?a)) (not (IZ ?r ?a))))
                (forall(?r - row) (when (and (not (IZ ?r ?a)) (IX ?r ?a))      (IZ ?r ?a)))
              )
)

;; Applying H gate on qubit a:
;; We only specify the condition where the proposition flips:
(:action h-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(IX ?r ?a))    (IZ ?r ?a))      (and     (IX ?r ?a) (not(IZ ?r ?a))) ))
                (forall(?r - row) (when (and     (IX ?r ?a) (not(IZ ?r ?a)))     (and (not(IX ?r ?a))    (IZ ?r ?a))  ))
              )
)

;; W mapped intermediate matrix elemets to main matrix elements:
;; This simluates swapping around to obtain the final goal condition:
(:action map-final
:parameters (?a ?b - qubit)
:precondition (and (not (imapped ?a)) (not (mapped ?b)))
:effect       (and
                ;; mapping IX on qubit a to X on qubit b:
                (forall(?r - row) (when (and      (IX ?r ?a))       (X ?r ?b)))
                (forall(?r - row) (when (and (not (IX ?r ?a))) (not (X ?r ?b))))
                ;; mapping IZ on qubit a to Z on qubit b:
                (forall(?r - row) (when (and      (IZ ?r ?a))       (Z ?r ?b)))
                (forall(?r - row) (when (and (not (IZ ?r ?a))) (not (Z ?r ?b))))
                ;; disabling mapped qubits:
                (imapped ?a) (mapped ?b)
                ;; stop all other actions once permutation started:
                (permuted )
              )
)

)
