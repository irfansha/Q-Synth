(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions)

(:types row qubit - object)

(:predicates
             ; busy qubits, all qubits start free i.e., not busy by default:
             (busy ?q - qubit)
             ; disable qubit after last single gate:
             (disabled ?q - qubit)
             ; single direction qubit pairs are enough, i.e., i < j when two qubits are chosen
             (ordered ?i ?j - qubit)
             ; to indicate single qubit gate to be applied in the next step:
             (apply_single_gate ?i - qubit)
             ; to indicate cnot gate to be applied in the next step:
             (apply_cnot_gate ?i - qubit)
             ; pauli X matrix element
             (X ?r - row ?c - qubit)
             ; pauli Z matrix element
             (Z ?r - row ?c - qubit)
)	

(:action choose
:parameters (?i ?j - qubit)
:precondition (and (ordered ?i ?j)
                   (not (busy ?i)) (not (busy ?j))
                   (not (disabled ?i)) (not (disabled ?j))
                   )
:effect       (and
                (busy ?i) (busy ?j)
                (apply_single_gate ?i) (apply_single_gate ?j)
              )
)


;; Applying I gate on qubit i:
(:action i-gate
:parameters (?i - qubit)
:precondition (and (busy ?i) (not (disabled ?i)) (apply_single_gate ?i))
:effect       (and (not (apply_single_gate ?i))
                   (apply_cnot_gate ?i)
              )
)

;; Applying HS gate on qubit i:
(:action hs-gate
:parameters (?i - qubit)
:precondition (and (busy ?i) (not (disabled ?i)) (apply_single_gate ?i))
:effect       (and
                (not (apply_single_gate ?i))
                (apply_cnot_gate ?i)
                ;; x_i = z_i
                (forall(?r - row) (when (and      (Z ?r ?i))       (X ?r ?i)))
                (forall(?r - row) (when (and (not (Z ?r ?i))) (not (X ?r ?i))))
                ;; z_i = z_i XOR x_i
                (forall(?r - row) (when (and      (Z ?r ?i)  (X ?r ?i)) (not (Z ?r ?i))))
                (forall(?r - row) (when (and (not (Z ?r ?i)) (X ?r ?i))      (Z ?r ?i)))
              )
)

;; Applying SH gate on qubit i:
(:action sh-gate
:parameters (?i - qubit)
:precondition (and (busy ?i) (not (disabled ?i)) (apply_single_gate ?i))
:effect       (and
                (not (apply_single_gate ?i))
                (apply_cnot_gate ?i)
                ;; x_i = x_i + z_i
                (forall(?r - row) (when (and      (X ?r ?i)  (Z ?r ?i)) (not (X ?r ?i))))
                (forall(?r - row) (when (and (not (X ?r ?i)) (Z ?r ?i))      (X ?r ?i)))
                ;; z_i = x_i
                (forall(?r - row) (when (and      (X ?r ?i))       (Z ?r ?i)))
                (forall(?r - row) (when (and (not (X ?r ?i))) (not (Z ?r ?i))))
              )
)

;; applying CNOT gate from qubit i to j:
;; we only change the proposition that actually change, rest are propagated implicitly:
(:action cnot
:parameters (?i ?j - qubit)
:precondition (and (ordered ?i ?j)
                   (busy ?i) (busy ?j)
                   (not (disabled ?i)) (not (disabled ?j))
                   (apply_cnot_gate ?i) (apply_cnot_gate ?j)
              )
:effect       (and
                (not (apply_cnot_gate ?i)) (not (apply_cnot_gate ?j))
                (not (busy ?i)) (not (busy ?j))
                ;; x_j = x_i XOR x_j
                (forall(?r - row) (when (and (X ?r ?i)      (X ?r ?j))  (not (X ?r ?j))))
                (forall(?r - row) (when (and (X ?r ?i) (not (X ?r ?j)))      (X ?r ?j)))
                ;; z_i = z_i XOR z_j
                (forall(?r - row) (when (and      (Z ?r ?i)  (Z ?r ?j)) (not (Z ?r ?i))))
                (forall(?r - row) (when (and (not (Z ?r ?i)) (Z ?r ?j))      (Z ?r ?i)))
              )
)

;; ==================================================================
;; Layer single qubit gates layer actions:
;; apply a gate and disable that qubit:
;; ==================================================================

;; Applying I gate:
(:action i-gate-last
:parameters (?i - qubit)
:precondition (and (not (disabled ?i)) (not (busy ?i)))
:effect       (and (disabled ?i))
)

;; Applying S gate:
(:action s-gate-last
:parameters (?i - qubit)
:precondition (and (not (disabled ?i)) (not (busy ?i)))
:effect       (and
                (disabled ?i)
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?i)  (X ?r ?i)) (not (Z ?r ?i))))
                (forall(?r - row) (when (and (not (Z ?r ?i)) (X ?r ?i))      (Z ?r ?i)))
              )
)

;; Applying H gate on qubit a:
;; We only specify the condition where the proposition flips:
(:action h-gate-last
:parameters (?i - qubit)
:precondition (and (not (disabled ?i)) (not (busy ?i)))
:effect       (and
                (disabled ?i)
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(X ?r ?i))    (Z ?r ?i))      (and     (X ?r ?i) (not(Z ?r ?i))) ))
                (forall(?r - row) (when (and     (X ?r ?i) (not(Z ?r ?i)))     (and (not(X ?r ?i))    (Z ?r ?i))  ))
              )
)

;; Applying HS gate on qubit i:
(:action hs-gate-last
:parameters (?i - qubit)
:precondition (and (not (disabled ?i)) (not (busy ?i)))
:effect       (and
                (disabled ?i)
                ;; x_i = z_i
                (forall(?r - row) (when (and      (Z ?r ?i))       (X ?r ?i)))
                (forall(?r - row) (when (and (not (Z ?r ?i))) (not (X ?r ?i))))
                ;; z_i = z_i XOR x_i
                (forall(?r - row) (when (and      (Z ?r ?i)  (X ?r ?i)) (not (Z ?r ?i))))
                (forall(?r - row) (when (and (not (Z ?r ?i)) (X ?r ?i))      (Z ?r ?i)))
              )
)

;; Applying SH gate on qubit i:
(:action sh-gate-last
:parameters (?i - qubit)
:precondition (and (not (disabled ?i)) (not (busy ?i)))
:effect       (and
                (disabled ?i)
                ;; x_i = x_i + z_i
                (forall(?r - row) (when (and      (X ?r ?i)  (Z ?r ?i)) (not (X ?r ?i))))
                (forall(?r - row) (when (and (not (X ?r ?i)) (Z ?r ?i))      (X ?r ?i)))
                ;; z_i = x_i
                (forall(?r - row) (when (and      (X ?r ?i))       (Z ?r ?i)))
                (forall(?r - row) (when (and (not (X ?r ?i))) (not (Z ?r ?i))))
              )
)

;; Applying HSH gate on qubit i:
(:action hsh-gate-last
:parameters (?i - qubit)
:precondition (and (not (disabled ?i)) (not (busy ?i)))
:effect       (and
                (disabled ?i)
                ;; x_i = x_i + z_i
                (forall(?r - row) (when (and      (X ?r ?i)  (Z ?r ?i)) (not (X ?r ?i))))
                (forall(?r - row) (when (and (not (X ?r ?i)) (Z ?r ?i))      (X ?r ?i)))
              )
)

)
