OPENQASM 2.0;
include "qelib1.inc";
qreg q[54];
creg c[4];
cx q[13],q[7];
cx q[7],q[1];
cx q[1],q[6];
cx q[6],q[13];
