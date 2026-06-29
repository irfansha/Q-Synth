(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions :action-costs)

(:types row qubit gate - object)

(:predicates
            (X ?r - row ?c - qubit)            ; pauli X matrix element
            (Z ?r - row ?c - qubit)            ; pauli Z matrix element
            (done ?g - gate)                   ; gate ?g has been applied, initially all false and goal is to get them all true
            ; static predicates
            (oneq_gate ?g - gate ?a - qubit)                   ; single qubit gate ?g on qubit a
            (cnot_gate ?g - gate ?a ?b - qubit)                 ; CNOT gate ?g from qubit a to b
            (depends ?prev_g ?cur_g - gate)          ; gate ?prev_g depends on gate ?cur_g (i.e., cur_g must be done before prev_g can be applied)
            (flip_cnot)                                 ; to indicate whether to allow CNOT direction flip or not
)

(:functions
  (total-cost) - number
)

;; applying CNOT gate from qubit a to b:
(:action cnot
:parameters (?a ?b - qubit ?prev_g ?cur_g - gate)
:precondition (and
                (cnot_gate ?cur_g ?a ?b) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; x_b = x_a XOR x_b
                (forall(?r - row) (when (and (X ?r ?a)      (X ?r ?b))  (not (X ?r ?b))))
                (forall(?r - row) (when (and (X ?r ?a) (not (X ?r ?b)))      (X ?r ?b)))
                ;; z_a = z_a XOR z_b
                (forall(?r - row) (when (and      (Z ?r ?a)  (Z ?r ?b)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (Z ?r ?b))      (Z ?r ?a)))
                ;; mark gate cur_g as done
                (done ?cur_g)
                (increase (total-cost) 1)
              )
)

;; applying CNOT gate from qubit a to b:
(:action cnot-flipped
:parameters (?a ?b - qubit ?prev_g ?cur_g - gate)
:precondition (and
                (flip_cnot)
                (cnot_gate ?cur_g ?b ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; x_b = x_a XOR x_b
                (forall(?r - row) (when (and (X ?r ?a)      (X ?r ?b))  (not (X ?r ?b))))
                (forall(?r - row) (when (and (X ?r ?a) (not (X ?r ?b)))      (X ?r ?b)))
                ;; z_a = z_a XOR z_b
                (forall(?r - row) (when (and      (Z ?r ?a)  (Z ?r ?b)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (Z ?r ?b))      (Z ?r ?a)))
                ;; mark gate cur_g as done
                (done ?cur_g)
                (increase (total-cost) 1)
              )
)

;; Applying I gate on qubit i:
(:action i-gate
:parameters (?a - qubit ?prev_g ?cur_g - gate)
:precondition (and 
                (oneq_gate ?cur_g ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and 
                (done ?cur_g)
                (increase (total-cost) 0)
              )
)

;; Applying S gate on qubit a:
(:action s-gate
:parameters (?a - qubit ?prev_g ?cur_g - gate)
:precondition (and 
                (oneq_gate ?cur_g ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
                (done ?cur_g)
                (increase (total-cost) 1)
              )
)

;; Applying H gate on qubit a:
(:action h-gate
:parameters (?a - qubit ?prev_g ?cur_g - gate)
:precondition (and 
                (oneq_gate ?cur_g ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(X ?r ?a))    (Z ?r ?a))      (and     (X ?r ?a) (not(Z ?r ?a))) ))
                (forall(?r - row) (when (and     (X ?r ?a) (not(Z ?r ?a)))     (and (not(X ?r ?a))    (Z ?r ?a))  ))
                (done ?cur_g)
                (increase (total-cost) 1)
              )
)

;; Applying HS gate on qubit a:
(:action hs-gate
:parameters (?a - qubit ?prev_g ?cur_g - gate)
:precondition (and 
                (oneq_gate ?cur_g ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; x_a = z_a
                (forall(?r - row) (when (and      (Z ?r ?a))       (X ?r ?a)))
                (forall(?r - row) (when (and (not (Z ?r ?a))) (not (X ?r ?a))))
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
                (done ?cur_g)
                (increase (total-cost) 2)
              )
)

;; Applying SH gate on qubit a:
(:action sh-gate
:parameters (?a - qubit ?prev_g ?cur_g - gate)
:precondition (and 
                (oneq_gate ?cur_g ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; x_a = x_a + z_a
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                ;; z_a = x_a
                (forall(?r - row) (when (and      (X ?r ?a))       (Z ?r ?a)))
                (forall(?r - row) (when (and (not (X ?r ?a))) (not (Z ?r ?a))))
                (done ?cur_g)
                (increase (total-cost) 2)
              )
)

;; Applying Sx gate on qubit a:
;; Sx = S H S
(:action sx-gate
:parameters (?a - qubit ?prev_g ?cur_g - gate)
:precondition (and 
                (oneq_gate ?cur_g ?a) (depends ?cur_g ?prev_g)
                (done ?prev_g) (not (done ?cur_g))
              )
:effect       (and
                ;; x_a = z_a XOR x_a
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                (done ?cur_g)
                (increase (total-cost) 1)
              )
)

)
