(define (domain Clifford-Synthesis)
(:requirements :conditional-effects :typing :equality :negative-preconditions)

(:types row qubit - object)

(:predicates ;; pauli X matrix element
             (X ?r - row ?c - qubit)
             ;; pauli Z matrix element
             (Z ?r - row ?c - qubit)
             ;; phase matrix element
             (P ?r - row)
             ;; static predicate for X Z row connection
             (rpair ?r1 ?r2 - row)
             ;; if a row is mapped
             (rmapped ?r - row)
             ;; if a qubit is mapped
             (qmapped ?c - qubit)
)

;; we permutate the initial matrix
;; we simply initialize a permuted matrix by setting each qubit at a time
(:action map-initial
:parameters (?r1 ?r2 - row ?a - qubit)
:precondition (and
                ;; rows and qubit chosen must be not mapped before and rows must be a pair in X, Z matrix:
                (rpair ?r1 ?r2) (not (rmapped ?r1)) (not (rmapped ?r2)) (not (qmapped ?a))
                (not (X ?r1 ?a)) (not (Z ?r2 ?a))
              )
:effect       (and
                ;; setting X, Z matrix elements to true i.e., initializing qubits:
                (X ?r1 ?a) (Z ?r2 ?a)
                ;; declaring rows and the qubit as mapped:
                (rmapped ?r1) (rmapped ?r2) (qmapped ?a)
              )
)


;; applying CNOT gate from qubit a to b:
;; we only change the proposition that actually change, rest are propagated implicitly:
(:action cnot
:parameters (?a ?b - qubit)
:precondition (and (not (= ?a ?b)) (qmapped ?a) (qmapped ?b))
:effect       (and
                ;; x_b = x_a XOR x_b
                (forall(?r - row) (when (and (X ?r ?a)      (X ?r ?b))  (not (X ?r ?b))))
                (forall(?r - row) (when (and (X ?r ?a) (not (X ?r ?b)))      (X ?r ?b)))
                ;; z_a = z_a XOR z_b
                (forall(?r - row) (when (and      (Z ?r ?a)  (Z ?r ?b)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (Z ?r ?b))      (Z ?r ?a)))
                ;;                                          p   = p XOR (x_a*z_b (x_b XOR z_a XOR 1))
                ;;                                                partial revelant truth table:
                ;;                             x_ra           x_rb           z_ra       z_rb        p_r      =   p_r
                ;;                              1	       0	      0	         1	     0	          1
                (forall(?r - row) (when (and (X ?r ?a) (not(X ?r ?b)) (not(Z ?r ?a)) (Z ?r ?b) (not(P ?r)))     (P ?r)))
                ;;                              1	       0	      0	         1	     1	          0
                (forall(?r - row) (when (and (X ?r ?a) (not(X ?r ?b)) (not(Z ?r ?a)) (Z ?r ?b)     (P ?r))  (not(P ?r))))
                ;;                              1	       1	      1	         1	     0	          1
                (forall(?r - row) (when (and (X ?r ?a)     (X ?r ?b)      (Z ?r ?a)  (Z ?r ?b) (not(P ?r)))     (P ?r)))
                ;;                              1	       1	      1	         1	     1	          0
                (forall(?r - row) (when (and (X ?r ?a)     (X ?r ?b)      (Z ?r ?a)  (Z ?r ?b)     (P ?r))  (not(P ?r))))
              )
)

;; Applying S gate on qubit a:
;; Similar to CNOT, we only specify the condition where the proposition flips:
(:action s-gate
:parameters (?a - qubit)
:precondition (and (qmapped ?a))
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a)
                ;;                                 partial revelant truth table:
		;;              	       x_ra    z_ra      p_r            p_r
                ;;				1	  1	   0	          1
                (forall(?r - row) (when (and (X ?r ?a) (Z ?r ?a) (not(P ?r)))  (P ?r)))
		;;				1	  1	   1	          0
                (forall(?r - row) (when (and (X ?r ?a) (Z ?r ?a) (P ?r))      (not(P ?r))))
              )
)

;; Applying H gate on qubit a:
;; We only specify the condition where the proposition flips:
(:action h-gate
:parameters (?a - qubit)
:precondition (and (qmapped ?a))
:effect       (and
                ;; x_a swap with z_a
                (forall(?r - row) (when (and (not(X ?r ?a))    (Z ?r ?a))      (and     (X ?r ?a) (not(Z ?r ?a))) ))
                (forall(?r - row) (when (and     (X ?r ?a) (not(Z ?r ?a)))     (and (not(X ?r ?a))    (Z ?r ?a))  ))
                ;;                                   p   = p XOR (x_a*z_a)
                ;;                                 partial revelant truth table:
		;;              	       x_ra    z_ra           p_r            p_r
                ;;				1	  1	       0	     1
                (forall(?r - row) (when (and (X ?r ?a) (Z ?r ?a) (not(P ?r)))      (P ?r)))
		;;				1	  1	       1	     0
                (forall(?r - row) (when (and (X ?r ?a) (Z ?r ?a)     (P ?r))   (not(P ?r))))
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
:precondition (and (qmapped ?a))
:effect       (and
                ;;                                   p   = p XOR z_a
                (forall(?r - row) (when (and      (P ?r)  (Z ?r ?a)) (not (P ?r))))
                (forall(?r - row) (when (and (not (P ?r)) (Z ?r ?a))      (P ?r)))
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
:precondition (and (qmapped ?a))
:effect       (and
                ;;                                   p   = p XOR x_a XOR z_a
                ;;                                     0	0	       1               1
                (forall(?r - row) (when (and (not (P ?r)) (not(X ?r ?a))    (Z ?r ?a))      (P ?r)))
                ;;                                     0	1	       0	       1
                (forall(?r - row) (when (and (not (P ?r))     (X ?r ?a) (not(Z ?r ?a)))     (P ?r)))
                ;;                                     1	0	       1	       0
                (forall(?r - row) (when (and      (P ?r)  (not(X ?r ?a))    (Z ?r ?a))  (not(P ?r))))
                ;;                                     1	1	       0	       0
                (forall(?r - row) (when (and      (P ?r)      (X ?r ?a) (not(Z ?r ?a))) (not(P ?r))))
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
:precondition (and (qmapped ?a))
:effect       (and
                ;;                                   p   = p XOR x_a
                (forall(?r - row) (when (and      (P ?r)  (X ?r ?a)) (not (P ?r))))
                (forall(?r - row) (when (and (not (P ?r)) (X ?r ?a))      (P ?r)))
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
:precondition (and (qmapped ?a))
:effect       (and
                ;; z_a = z_a XOR x_a
                (forall(?r - row) (when (and      (Z ?r ?a)  (X ?r ?a)) (not (Z ?r ?a))))
                (forall(?r - row) (when (and (not (Z ?r ?a)) (X ?r ?a))      (Z ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a) XOR x
                ;;                                 partial revelant truth table:
		;;                                 p_r	    x_ra	  z_ra	         p_r
		;;                                  0	     1	           0	          1
                (forall(?r - row) (when (and (not(P ?r)) (X ?r ?a) (not(Z ?r ?a)))      (P ?r)))
		;;                                  1	     1	           0	          0
                (forall(?r - row) (when (and     (P ?r)  (X ?r ?a) (not(Z ?r ?a)))  (not(P ?r))))
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
:precondition (and (qmapped ?a))
:effect       (and
                ;; x_a = z_a XOR x_a
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a) XOR z
                ;;                                 partial revelant truth table:
		;;                                 p_r	    z_ra	  x_ra	         p_r
		;;                                  0	     1	           0	          1
                (forall(?r - row) (when (and (not(P ?r)) (Z ?r ?a) (not(X ?r ?a)))      (P ?r)))
		;;                                  1	     1	           0	          0
                (forall(?r - row) (when (and     (P ?r)  (Z ?r ?a) (not(X ?r ?a)))  (not(P ?r))))
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
:precondition (and (qmapped ?a))
:effect       (and
                ;; x_a = z_a XOR x_a
                (forall(?r - row) (when (and      (X ?r ?a)  (Z ?r ?a)) (not (X ?r ?a))))
                (forall(?r - row) (when (and (not (X ?r ?a)) (Z ?r ?a))      (X ?r ?a)))
                ;;                                   p   = p XOR (x_a*z_a)
                ;;                                 partial revelant truth table:
		;;              	       x_ra    z_ra      p_r            p_r
                ;;				1	  1	   0	          1
                (forall(?r - row) (when (and (X ?r ?a) (Z ?r ?a) (not(P ?r)))  (P ?r)))
		;;				1	  1	   1	          0
                (forall(?r - row) (when (and (X ?r ?a) (Z ?r ?a) (P ?r))      (not(P ?r))))
              )
)

)
