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
             ; phase matrix element
             (P ?r - row)
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
                ;;                                          p   = p XOR (x_a*z_b (x_b XOR z_a XOR 1))
                ;;                                                partial revelant truth table:
                ;;                             x_ra           x_rb           z_ra       z_rb        p_r      =   p_r
                ;;                              1	       0	      0	         1	     0	          1
                (forall(?r - row) (when (and (IX ?r ?a) (not(IX ?r ?b)) (not(IZ ?r ?a)) (IZ ?r ?b) (not(P ?r)))     (P ?r)))
                ;;                              1	       0	      0	         1	     1	          0
                (forall(?r - row) (when (and (IX ?r ?a) (not(IX ?r ?b)) (not(IZ ?r ?a)) (IZ ?r ?b)     (P ?r))  (not(P ?r))))
                ;;                              1	       1	      1	         1	     0	          1
                (forall(?r - row) (when (and (IX ?r ?a)     (IX ?r ?b)      (IZ ?r ?a)  (IZ ?r ?b) (not(P ?r)))     (P ?r)))
                ;;                              1	       1	      1	         1	     1	          0
                (forall(?r - row) (when (and (IX ?r ?a)     (IX ?r ?b)      (IZ ?r ?a)  (IZ ?r ?b)     (P ?r))  (not(P ?r))))
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
                ;;                                   p   = p XOR (x_a*z_a)
                ;;                                 partial revelant truth table:
		;;              	       x_ra    z_ra      p_r            p_r
                ;;				1	  1	   0	          1
                (forall(?r - row) (when (and (IX ?r ?a) (IZ ?r ?a) (not(P ?r)))  (P ?r)))
		;;				1	  1	   1	          0
                (forall(?r - row) (when (and (IX ?r ?a) (IZ ?r ?a) (P ?r))      (not(P ?r))))
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
                ;;                                   p   = p XOR (x_a*z_a)
                ;;                                 partial revelant truth table:
		;;              	       x_ra    z_ra           p_r            p_r
                ;;				1	  1	       0	     1
                (forall(?r - row) (when (and (IX ?r ?a) (IZ ?r ?a) (not(P ?r)))      (P ?r)))
		;;				1	  1	       1	     0
                (forall(?r - row) (when (and (IX ?r ?a) (IZ ?r ?a)     (P ?r))   (not(P ?r))))
              )
)

;; Applying X gate on qubit a:
;; =============
;; -------------
;; X = H S S H
;; -------------
;; =============
;; We only specify the condition where the proposition flips:
(:action x-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;;                                   p   = p XOR z_a
                (forall(?r - row) (when (and      (P ?r)  (IZ ?r ?a)) (not (P ?r))))
                (forall(?r - row) (when (and (not (P ?r)) (IZ ?r ?a))      (P ?r)))
              )
)

;; Applying Y gate on qubit a:
;; =============
;; -------------
;; Y = X Z
;; -------------
;; =============
;; We only specify the condition where the proposition flips:
(:action y-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;;                                   p   = p XOR x_a XOR z_a
                ;;                                     0	0	       1               1
                (forall(?r - row) (when (and (not (P ?r)) (not(IX ?r ?a))    (IZ ?r ?a))      (P ?r)))
                ;;                                     0	1	       0	       1
                (forall(?r - row) (when (and (not (P ?r))     (IX ?r ?a) (not(IZ ?r ?a)))     (P ?r)))
                ;;                                     1	0	       1	       0
                (forall(?r - row) (when (and      (P ?r)  (not(IX ?r ?a))    (IZ ?r ?a))  (not(P ?r))))
                ;;                                     1	1	       0	       0
                (forall(?r - row) (when (and      (P ?r)      (IX ?r ?a) (not(IZ ?r ?a))) (not(P ?r))))
              )
)

;; Applying Z gate on qubit a:
;; =============
;; -------------
;; Z = S S
;; -------------
;; =============
;; We only specify the condition where the proposition flips:
(:action z-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;;                                   p   = p XOR x_a
                (forall(?r - row) (when (and      (P ?r)  (IX ?r ?a)) (not (P ?r))))
                (forall(?r - row) (when (and (not (P ?r)) (IX ?r ?a))      (P ?r)))
              )
)

;; Applying S-dagger gate on qubit a:
;; =============
;; -------------
;; Sdg = Z S
;; -------------
;; =============
;; we only specify the condition where the proposition flips:
(:action sdg-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (IZ ?r ?a)  (IX ?r ?a)) (not (IZ ?r ?a))))
                (forall(?r - row) (when (and (not (IZ ?r ?a)) (IX ?r ?a))      (IZ ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a) XOR x
                ;;                                 partial revelant truth table:
		;;                                 p_r	    x_ra	  z_ra	         p_r
		;;                                  0	     1	           0	          1
                (forall(?r - row) (when (and (not(P ?r)) (IX ?r ?a) (not(IZ ?r ?a)))      (P ?r)))
		;;                                  1	     1	           0	          0
                (forall(?r - row) (when (and     (P ?r)  (IX ?r ?a) (not(IZ ?r ?a)))  (not(P ?r))))
              )
)

;; Applying Sx gate on qubit a:
;; =============
;; -------------
;; X = Sdg H Sdg
;; -------------
;; =============
;; we only specify the condition where the proposition flips:
(:action sx-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;; x_a = z_a XOR x_a
                (forall(?r - row) (when (and      (IX ?r ?a)  (IZ ?r ?a)) (not (IX ?r ?a))))
                (forall(?r - row) (when (and (not (IX ?r ?a)) (IZ ?r ?a))      (IX ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a) XOR z
                ;;                                 partial revelant truth table:
		;;                                 p_r	    z_ra	  x_ra	         p_r
		;;                                  0	     1	           0	          1
                (forall(?r - row) (when (and (not(P ?r)) (IZ ?r ?a) (not(IX ?r ?a)))      (P ?r)))
		;;                                  1	     1	           0	          0
                (forall(?r - row) (when (and     (P ?r)  (IZ ?r ?a) (not(IX ?r ?a)))  (not(P ?r))))
              )
)

;; Applying Sx-Dagger gate on qubit a:
;; =============
;; -------------
;; Sxdg = S H S
;; -------------
;; =============
;; we only specify the condition where the proposition flips:
(:action sxdg-gate
:parameters (?a - qubit)
:precondition (and (not (permuted)))
:effect       (and
                ;; x_a = z_a XOR x_a
                (forall(?r - row) (when (and      (IX ?r ?a)  (IZ ?r ?a)) (not (IX ?r ?a))))
                (forall(?r - row) (when (and (not (IX ?r ?a)) (IZ ?r ?a))      (IX ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a)
                ;;                                 partial revelant truth table:
		;;              	       x_ra    z_ra      p_r            p_r
                ;;				1	  1	   0	          1
                (forall(?r - row) (when (and (IX ?r ?a) (IZ ?r ?a) (not(P ?r)))  (P ?r)))
		;;				1	  1	   1	          0
                (forall(?r - row) (when (and (IX ?r ?a) (IZ ?r ?a) (P ?r))      (not(P ?r))))
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
