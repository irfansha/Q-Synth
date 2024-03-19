; (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

; Planning Domain for Optimal Quantum Layout Mapping (lifted version)
; - initial mapping is integrated in the first CNOT
; - ancillary swaps are allowed, even before initial mapping
; - logical qubits allow multiple (relaxed) dependencies

(define (domain quantum)

(:requirements :strips :typing :negative-preconditions :universal-preconditions :disjunctive-preconditions)

(:types 
    pbit - object   ; physical qubit
    gate - object   ; gate (binary gate or input gate)
    lbit - gate)    ; logical qubit

(:predicates
    ; logical qubit ?l is currently mapped on physical qubit ?p
    (mapped ?l - lbit ?p - pbit)

    ; physical qubit ?p is occupied
    (occupied ?p - pbit)                        

    ; physical qubits ?p1 and ?p2 are connected;
    ; static predicate
    (connected ?p1 ?p2 - pbit)                 

    ; gate ?g0 on logical qubits ?l1 and ?l2 depends on gates ?g1 and ?g2
    ; static predicate
    (cnot ?l1 ?l2 - lbit ?g0 - gate)   

    (ctrl_depends ?g1 ?g2 - gate)
    (data_depends ?g1 ?g2 - gate)

    ; gate ?g has been applied (or mapped in case of input gate)
    ; initially all false, goal is to get them all true
    (done ?g - gate)                        
)

(:action apply_cnot_gate_gate
    :parameters (?l1 ?l2 - lbit ?p1 ?p2 - pbit ?g0 - gate)
    :precondition (and
        (cnot ?l1 ?l2 ?g0)
        (forall (?g1 - gate) 
            (imply (ctrl_depends ?g0 ?g1) (done ?g1))
        )
        (forall (?g2 - gate) 
           (imply (data_depends ?g0 ?g2) (done ?g2))
        )
        (connected ?p1 ?p2)
        (mapped ?l1 ?p1) (mapped ?l2 ?p2)
        (not (done ?g0))
    )
    :effect (and
        (done ?g0)
    )
)

(:action apply_cnot_input_input
    :parameters (?l1 ?l2 - lbit ?p1 ?p2 - pbit ?g0 - gate)
    :precondition (and
        (cnot ?l1 ?l2 ?g0)
        (connected ?p1 ?p2)
        (forall (?g1 - gate) (not (ctrl_depends ?g0 ?g1)))
        (forall (?g2 - gate) (not (data_depends ?g0 ?g2)))
        (not (occupied ?p1)) (not (occupied ?p2))
        (not (done ?g0)) (not (done ?l1)) (not (done ?l2))
    )
    :effect (and
        (done ?g0) (done ?l1) (done ?l2)
        (mapped ?l1 ?p1) (occupied ?p1)
        (mapped ?l2 ?p2) (occupied ?p2)
    )
)

(:action apply_cnot_input_gate
    :parameters (?l1 ?l2 - lbit ?p1 ?p2 - pbit ?g0 - gate)
    :precondition (and
        (cnot ?l1 ?l2 ?g0)
        (connected ?p1 ?p2)
        (mapped ?l2 ?p2)
        (not (occupied ?p1))
        (forall (?g1 - gate) (not (ctrl_depends ?g0 ?g1)))
        (forall (?g2 - gate) 
            (imply (data_depends ?g0 ?g2) (done ?g2))
        )
        (not (done ?g0)) (not (done ?l1))
    )
    :effect (and
        (done ?g0) (done ?l1)
        (mapped ?l1 ?p1) (occupied ?p1)
    )
)

(:action apply_cnot_gate_input
    :parameters (?l1 ?l2 - lbit ?p1 ?p2 - pbit ?g0 - gate)
    :precondition (and
        (cnot ?l1 ?l2 ?g0)
        (connected ?p1 ?p2)
        (mapped ?l1 ?p1)
        (not (occupied ?p2))
        (forall (?g1 - gate) 
            (imply (ctrl_depends ?g0 ?g1) (done ?g1))
        )
        (forall (?g2 - gate) (not (data_depends ?g0 ?g2)))
        (not (done ?g0)) (not (done ?l2))
    )
    :effect (and
        (done ?g0) (done ?l2)
        (mapped ?l2 ?p2) (occupied ?p2)
    )
)

(:action swap11
    :parameters (?l1 ?l2 - lbit ?p1 ?p2 - pbit)
    :precondition (and 
        (connected ?p1 ?p2)
        (mapped ?l1 ?p1) (mapped ?l2 ?p2)
    )
    :effect (and 
        (mapped ?l1 ?p2) (not (mapped ?l1 ?p1))
        (mapped ?l2 ?p1) (not (mapped ?l2 ?p2))
    )
)

(:action swap10
    :parameters (?l1 - lbit ?p1 ?p2 - pbit)
    :precondition (and 
        (connected ?p1 ?p2)
        (mapped ?l1 ?p1)
        (not (occupied ?p2))
    )
    :effect (and 
        (not (mapped ?l1 ?p1)) (not (occupied ?p1))
        (mapped ?l1 ?p2) (occupied ?p2)
    )    
)

(:action swap01
    :parameters (?l2 - lbit ?p1 ?p2 - pbit)
    :precondition (and 
        (connected ?p1 ?p2)
        (mapped ?l2 ?p2)
        (not (occupied ?p1))
    )
    :effect (and 
        (not (mapped ?l2 ?p2)) (not (occupied ?p2))
        (mapped ?l2 ?p1) (occupied ?p1)
    )    
)

)
