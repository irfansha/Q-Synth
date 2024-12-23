(define (problem instance)
  (:domain Cnot-Synthesis)
  (:objects  q0 q1 q2 q3 q4 q5 q6 q7 q8 - qubit)
(:init

;; Indentity matrix
(X q0 q0)
(X q1 q1)
(X q2 q2)
(X q3 q3)
(X q4 q4)
(X q5 q5)
(X q6 q6)
(X q7 q7)
(X q8 q8)
)
(:goal
  (and
   ;; target destabilizer X matrix
      (X q0 q0) (not (X q0 q1))(not (X q0 q2))(not (X q0 q3))(not (X q0 q4))     (X q0 q5) (not (X q0 q6))(not (X q0 q7))(not (X q0 q8))
 (not (X q1 q0))     (X q1 q1) (not (X q1 q2))(not (X q1 q3))(not (X q1 q4))(not (X q1 q5))(not (X q1 q6))(not (X q1 q7))(not (X q1 q8))
 (not (X q2 q0))(not (X q2 q1))     (X q2 q2) (not (X q2 q3))(not (X q2 q4))     (X q2 q5) (not (X q2 q6))(not (X q2 q7))(not (X q2 q8))
 (not (X q3 q0))(not (X q3 q1))(not (X q3 q2))     (X q3 q3) (not (X q3 q4))(not (X q3 q5))(not (X q3 q6))(not (X q3 q7))(not (X q3 q8))
 (not (X q4 q0))(not (X q4 q1))(not (X q4 q2))(not (X q4 q3))     (X q4 q4) (not (X q4 q5))(not (X q4 q6))(not (X q4 q7))(not (X q4 q8))
 (not (X q5 q0))(not (X q5 q1))(not (X q5 q2))(not (X q5 q3))(not (X q5 q4))     (X q5 q5) (not (X q5 q6))(not (X q5 q7))(not (X q5 q8))
 (not (X q6 q0))(not (X q6 q1))(not (X q6 q2))(not (X q6 q3))(not (X q6 q4))(not (X q6 q5))     (X q6 q6) (not (X q6 q7))(not (X q6 q8))
 (not (X q7 q0))(not (X q7 q1))(not (X q7 q2))(not (X q7 q3))(not (X q7 q4))(not (X q7 q5))(not (X q7 q6))     (X q7 q7) (not (X q7 q8))
 (not (X q8 q0))(not (X q8 q1))(not (X q8 q2))(not (X q8 q3))(not (X q8 q4))(not (X q8 q5))(not (X q8 q6))(not (X q8 q7))     (X q8 q8) 
  )
)
)