// V. Gheorghiu, J. Huang, Sarah Meng Li, M. Mosca, P. Mukhopadhyay,
// Reducing the CNOT count for Clifford+T circuits on NISQ architectures.
// https://arxiv.org/abs/2011.12191v4, 10 Oct 2022. Appendix B, Figure 3, p. 28

OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
cx q[1],q[3];
cx q[2],q[1];
cx q[3],q[4];
cx q[3],q[5];
cx q[4],q[2];
cx q[0],q[3];
cx q[5],q[1];
cx q[4],q[0];
cx q[3],q[2];
cx q[2],q[4];

