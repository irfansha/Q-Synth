; (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

; Planning Domain for Optimal Quantum Layout Mapping (global version)
; - version with ancillary bits

(define (domain Quantum)
(:requirements :typing :negative-preconditions)
(:types pqubit lqubit depth)
(:constants d0 - depth)
(:predicates (occupied_pqubit ?p - pqubit)
             (occupied_lqubit ?l - lqubit)
             (mapped ?l - lqubit ?p - pqubit)
             (connected ?p1 ?p2 - pqubit)
             ;; required cnot(control_gate,target_gate) is described as follows at some depth
             (rcnot ?l1 ?l2 - lqubit ?d - depth)
             (current_depth ?d - depth)
             (next_depth ?d1 ?d2 - depth)
)

;; In the first step (or depth), the logical qubits to be mapped to some physical qubits
;; We use map initial action for such mapping
;; Since we need the initial mapping first, we use depth s0 with the very first depth

(:action map_initial
:parameters (?l - lqubit ?p - pqubit)
:precondition (and (not (occupied_lqubit ?l)) (not (occupied_pqubit ?p))) ; (current_depth d0))
:effect       (and (occupied_lqubit ?l) (occupied_pqubit ?p) (mapped ?l ?p))
)

;; In each depth, we need to satisfy some cnot operations
;; we use swap to swap the mapped logical qubits

(:action swap
:parameters (?l1 ?l2 - lqubit ?p1 ?p2 - pqubit)
:precondition (and (mapped ?l1 ?p1) (mapped ?l2 ?p2) (connected ?p1 ?p2)); (not (current_depth d0)))
:effect       (and (not (mapped ?l1 ?p1)) (not (mapped ?l2 ?p2)) (mapped ?l1 ?p2) (mapped ?l2 ?p1))
)

;; we can swap with ancillary qubits:
;; we update if qubits are initialized and occupied

(:action swap_ancillary
:parameters (?l1 - lqubit ?p1 ?p2 - pqubit)
:precondition (and (mapped ?l1 ?p1) (not (occupied_pqubit ?p2)) (connected ?p1 ?p2)); (not (current_depth d0)))
:effect       (and (not (mapped ?l1 ?p1)) (mapped ?l1 ?p2) (not (occupied_pqubit ?p1)) (occupied_pqubit ?p2))
)


;; After (full/partial) swapping, we need to apply cnot gates
;; only when the physical qubits to which the logical qubits are connected, we can apply the cnot gate in that time step

(:action apply_cnot
:parameters (?l1 ?l2 - lqubit ?p1 ?p2 - pqubit ?d - depth)
:precondition (and (mapped ?l1 ?p1) (mapped ?l2 ?p2) (connected ?p1 ?p2) (rcnot ?l1 ?l2 ?d) (current_depth ?d))
:effect       (and (not (rcnot ?l1 ?l2 ?d)))
)

;; Since unitary operators can be swapped (physically) along with qubits, we group cnots together and unitary operators together
;; these form depths, as long as the swapping is done for cnot at each depth the correctness is preserved
;; After each depth, we move to next depth

(:action move_depth
:parameters (?d1 ?d2 - depth) 
:precondition (and (current_depth ?d1) (next_depth ?d1 ?d2))
:effect       (and (not (current_depth ?d1)) (current_depth ?d2))
)

)
