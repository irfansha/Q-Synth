OPENQASM 2.0;
include "qelib1.inc";

qreg q[8];

// Layer 1: long-range CNOTs
cx q[0], q[7];
cx q[1], q[6];
cx q[2], q[5];
cx q[3], q[4];

// Layer 2: shifted connections
cx q[0], q[6];
cx q[1], q[5];
cx q[2], q[4];
cx q[3], q[7];

// Layer 3: cross mixing
cx q[0], q[4];
cx q[1], q[5];
cx q[2], q[6];
cx q[3], q[7];

// Layer 4: triangular mixing
cx q[0], q[1];
cx q[0], q[2];
cx q[1], q[3];
cx q[2], q[4];
cx q[3], q[5];
cx q[4], q[6];
cx q[5], q[7];

// Final scramble
cx q[1], q[6];
cx q[2], q[5];
cx q[3], q[4];