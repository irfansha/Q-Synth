// Sergey Bravyi, Joseph A. Latone, Dmitri Maslov
// 6-qubit Optimal Clifford Circuits
// https://arxiv.org/abs/2012.06074, Section 4, Fig. 3

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];

cx q[2],q[5];
cx q[5],q[2];
cx q[2],q[5];
cx q[2],q[1];
cx q[5],q[4];
cx q[4],q[5];
cx q[1],q[2];
cx q[1],q[0];
cx q[4],q[3];
cx q[3],q[4];
cx q[0],q[1];
cx q[0],q[3];
cx q[3],q[0];
cx q[0],q[3];
