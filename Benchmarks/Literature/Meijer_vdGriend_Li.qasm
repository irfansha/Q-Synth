// Arianne Meijer - van de Griend, Sarah Li
// Dynamic Qubit Routing with CNOT Circuit Synthesis for Quantum Compilation
// QPL 2022, Figure 11a, to be mapped on 6-qubit grid

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];

cx q[0],q[1];
cx q[1],q[5];
cx q[3],q[1];
cx q[1],q[4];
cx q[1],q[3];
cx q[3],q[5];
cx q[2],q[5];
cx q[5],q[4];
cx q[4],q[0];
cx q[0],q[2];

