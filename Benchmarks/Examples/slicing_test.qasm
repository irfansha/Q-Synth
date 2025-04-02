OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
x q[0];
cx q[1], q[2];
rx(0.12234) q[0];
rx(0.5*pi) q[0];
rx(0.15234) q[0];
