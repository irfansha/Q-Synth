OPENQASM 2.0;
include "qelib1.inc";
qreg q[80];
sx q[0];
rz(pi/2) q[1];
sx q[1];
cx q[1],q[0];
rz(1.0) q[0];
sx q[0];
rz(pi/2) q[1];
ry(0.9999999999999997) q[1];
cx q[1],q[0];
sx q[1];
rz(pi/2) q[1];
rz(pi/2) q[2];
sx q[2];
swap q[2],q[1];
x q[7];
sx q[12];
cx q[1],q[12];
rz(-pi) q[1];
rx(-1.0000000000000004) q[1];
rz(1.0) q[12];
rx(-pi/2) q[12];
cx q[1],q[12];
sx q[1];
rz(pi/2) q[1];
cx q[12],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
swap q[1],q[0];
cx q[0],q[7];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[12],q[13];
rz(-pi) q[12];
ry(-0.24999999999999994) q[12];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[12],q[13];
swap q[1],q[12];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[12];
swap q[1],q[12];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[12];
rz(pi/2) q[12];
sx q[12];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
swap q[13],q[12];
cx q[12],q[1];
ry(-pi/2) q[1];
rz(-pi) q[1];
rz(-pi) q[12];
ry(-0.24999999999999994) q[12];
swap q[14],q[13];
cx q[12],q[13];
ry(-0.2500000000000004) q[12];
rz(-pi/2) q[12];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[12],q[13];
cx q[13],q[14];
cx q[13],q[12];
rz(pi/2) q[12];
sx q[12];
swap q[1],q[12];
sx q[13];
rz(pi/2) q[14];
swap q[13],q[14];
cx q[13],q[12];
rz(pi/2) q[15];
sx q[15];
cx q[15],q[14];
rz(1.0) q[14];
x q[14];
rz(-pi) q[15];
rx(-1.0000000000000004) q[15];
cx q[15],q[14];
ry(-pi/2) q[14];
rz(-pi/2) q[14];
sx q[15];
rz(pi/2) q[15];
swap q[15],q[14];
cx q[14],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[0],q[13];
cx q[13],q[14];
ry(0.24999999999999972) q[13];
swap q[13],q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(pi/2) q[13];
sx q[13];
swap q[0],q[13];
cx q[13],q[14];
ry(0.24999999999999972) q[13];
swap q[13],q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(-pi/2) q[0];
cx q[0],q[13];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[0],q[7];
sx q[0];
cx q[1],q[0];
rz(2.0000000000000004) q[0];
x q[0];
rz(pi/2) q[1];
ry(1.9999999999999996) q[1];
cx q[1],q[0];
rz(pi/2) q[0];
sx q[0];
swap q[2],q[1];
rz(pi/2) q[13];
swap q[13],q[0];
cx q[0],q[1];
rz(pi/2) q[1];
rz(pi/2) q[14];
sx q[14];
swap q[14],q[13];
cx q[13],q[0];
rz(pi) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(-pi) q[0];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[0],q[7];
ry(-0.24999999999999972) q[0];
rz(-pi) q[0];
cx q[0],q[1];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.24999999999999972) q[0];
rz(-pi) q[0];
sx q[13];
rz(pi/2) q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.24999999999999972) q[0];
rz(-pi) q[0];
cx q[0],q[1];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(-pi/2) q[0];
rz(pi/2) q[1];
ry(-pi/2) q[7];
rz(-pi) q[7];
rz(pi/2) q[13];
sx q[13];
cx q[0],q[13];
cx q[0],q[7];
sx q[0];
rz(pi/2) q[13];
swap q[0],q[13];
cx q[0],q[1];
sx q[0];
cx q[12],q[1];
rz(pi/2) q[1];
cx q[14],q[13];
rz(-1.1415926535897931) q[13];
rx(-pi/2) q[13];
ry(1.141592653589794) q[14];
rz(-pi/2) q[14];
cx q[14],q[13];
sx q[14];
rz(pi/2) q[14];
swap q[15],q[14];
swap q[14],q[13];
cx q[13],q[0];
rz(1.0) q[0];
rx(-pi/2) q[0];
ry(-2.141592653589793) q[13];
rz(-pi/2) q[13];
cx q[13],q[0];
swap q[7],q[0];
sx q[13];
rz(pi/2) q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
cx q[13],q[12];
ry(-pi/2) q[12];
rz(-pi) q[12];
swap q[1],q[12];
ry(0.24999999999999972) q[13];
cx q[13],q[0];
ry(-0.2500000000000004) q[13];
cx q[13],q[12];
swap q[1],q[12];
ry(0.24999999999999972) q[13];
cx q[13],q[0];
ry(-0.2500000000000004) q[13];
cx q[13],q[12];
rz(pi/2) q[12];
sx q[12];
swap q[1],q[12];
ry(0.24999999999999972) q[13];
cx q[13],q[0];
ry(-0.2500000000000004) q[13];
cx q[13],q[12];
rz(pi/2) q[12];
swap q[1],q[12];
ry(0.24999999999999972) q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
ry(2.8915926535897927) q[13];
rz(-pi/2) q[13];
cx q[13],q[12];
rz(pi/2) q[12];
cx q[12],q[1];
cx q[2],q[1];
rz(10.42477796076938) q[1];
sx q[1];
ry(-2.141592653589793) q[2];
cx q[2],q[1];
sx q[2];
rz(pi/2) q[2];
swap q[12],q[1];
cx q[1],q[2];
rz(pi/2) q[2];
cx q[13],q[0];
cx q[0],q[7];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[14],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
swap q[14],q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(pi/2) q[13];
sx q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(2.891592653589793) q[0];
rz(-pi/2) q[0];
ry(-pi/2) q[7];
rz(-pi) q[7];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
cx q[0],q[7];
rz(pi/2) q[13];
cx q[13],q[14];
swap q[12],q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
swap q[13],q[12];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
cx q[1],q[0];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
ry(-pi/2) q[12];
rz(-pi) q[12];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
cx q[1],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.2500000000000004) q[1];
rz(-pi/2) q[1];
rz(pi/2) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
cx q[1],q[2];
rz(pi/2) q[12];
swap q[12],q[1];
cx q[1],q[0];
swap q[0],q[13];
sx q[1];
cx q[0],q[1];
rz(pi/2) q[1];
swap q[15],q[14];
cx q[14],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
cx q[0],q[1];
ry(-0.24999999999999972) q[0];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(-0.24999999999999994) q[0];
cx q[0],q[1];
ry(-0.2500000000000004) q[0];
swap q[14],q[13];
cx q[0],q[13];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
cx q[0],q[1];
ry(-0.24999999999999972) q[0];
rz(pi/2) q[13];
sx q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(-0.24999999999999994) q[0];
cx q[0],q[1];
ry(2.8915926535897927) q[0];
rz(pi/2) q[0];
rz(pi/2) q[1];
swap q[14],q[13];
cx q[0],q[13];
cx q[0],q[1];
cx q[7],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
rz(pi/2) q[13];
swap q[13],q[0];
cx q[0],q[7];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
swap q[0],q[13];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
swap q[13],q[0];
cx q[0],q[7];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
swap q[0],q[13];
rz(pi/2) q[7];
sx q[7];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
rz(-pi/2) q[13];
swap q[13],q[0];
cx q[0],q[7];
swap q[0],q[13];
rz(pi/2) q[7];
cx q[7],q[0];
rz(pi/2) q[0];
sx q[0];
ry(-pi/2) q[14];
rz(-pi) q[14];
cx q[13],q[14];
sx q[13];
cx q[0],q[13];
rz(pi/2) q[0];
ry(0.9999999999999997) q[0];
rz(4.141592653589793) q[13];
cx q[0],q[13];
sx q[0];
rz(pi/2) q[0];
swap q[0],q[1];
cx q[12],q[1];
rz(pi/2) q[1];
swap q[2],q[1];
rz(pi/2) q[14];
sx q[14];
swap q[14],q[13];
swap q[13],q[0];
cx q[0],q[1];
ry(pi/2) q[0];
rz(-0.9999999999999991) q[0];
rz(1.0) q[1];
cx q[1],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
sx q[1];
cx q[12],q[1];
ry(-pi/2) q[1];
rz(-pi) q[1];
rz(-pi) q[12];
ry(-0.24999999999999994) q[12];
swap q[12],q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
cx q[1],q[0];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
cx q[1],q[12];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
cx q[1],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.2500000000000004) q[1];
rz(-pi/2) q[1];
rz(pi/2) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
cx q[1],q[2];
sx q[1];
rz(pi/2) q[12];
swap q[12],q[1];
cx q[1],q[0];
rz(pi/2) q[0];
sx q[0];
cx q[0],q[13];
rx(-2.141592653589793) q[0];
cx q[1],q[2];
rz(pi/2) q[2];
rz(1.0) q[13];
rx(-pi/2) q[13];
cx q[0],q[13];
sx q[0];
rz(pi/2) q[0];
swap q[7],q[0];
swap q[15],q[14];
swap q[14],q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
swap q[13],q[12];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
cx q[1],q[0];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
ry(-pi/2) q[12];
rz(-pi) q[12];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
cx q[1],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
ry(-0.24999999999999972) q[1];
cx q[1],q[2];
ry(0.24999999999999972) q[1];
rz(-pi/2) q[1];
rz(pi/2) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
cx q[1],q[2];
swap q[0],q[1];
cx q[0],q[7];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[12],q[1];
swap q[1],q[0];
sx q[12];
swap q[14],q[13];
cx q[0],q[13];
cx q[0],q[1];
ry(0.24999999999999972) q[0];
ry(-pi/2) q[1];
rz(-pi) q[1];
ry(-pi/2) q[13];
rz(-pi) q[13];
cx q[0],q[13];
ry(-0.24999999999999972) q[0];
rz(-pi) q[0];
cx q[0],q[7];
ry(0.24999999999999972) q[0];
cx q[0],q[13];
ry(-0.2500000000000004) q[0];
cx q[0],q[1];
ry(0.24999999999999972) q[0];
cx q[0],q[13];
ry(-0.24999999999999972) q[0];
rz(-pi) q[0];
cx q[0],q[7];
ry(0.24999999999999972) q[0];
cx q[0],q[13];
ry(2.891592653589793) q[0];
rz(-pi/2) q[0];
rz(pi/2) q[1];
sx q[1];
cx q[0],q[1];
rz(pi/2) q[1];
ry(-pi/2) q[7];
rz(-pi) q[7];
ry(-pi/2) q[13];
rz(-pi) q[13];
cx q[0],q[13];
swap q[7],q[0];
cx q[1],q[0];
swap q[2],q[1];
cx q[13],q[14];
rz(pi/2) q[14];
swap q[15],q[14];
swap q[14],q[13];
cx q[0],q[13];
rz(pi/2) q[13];
swap q[0],q[13];
cx q[14],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[0],q[13];
rz(-pi) q[14];
ry(-0.24999999999999994) q[14];
cx q[14],q[15];
ry(-0.2500000000000004) q[14];
cx q[14],q[13];
rz(-pi) q[14];
ry(-0.24999999999999994) q[14];
cx q[14],q[15];
ry(-0.2500000000000004) q[14];
swap q[14],q[13];
cx q[13],q[0];
rz(pi/2) q[0];
sx q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
swap q[13],q[14];
cx q[14],q[15];
ry(-0.2500000000000004) q[14];
cx q[14],q[13];
rz(pi/2) q[13];
rz(-pi) q[14];
ry(-0.24999999999999994) q[14];
cx q[14],q[15];
ry(2.891592653589793) q[14];
rz(-pi/2) q[14];
swap q[14],q[13];
cx q[13],q[0];
swap q[13],q[14];
cx q[0],q[13];
sx q[0];
cx q[0],q[1];
rz(-pi/2) q[0];
ry(-1.0000000000000004) q[0];
rz(4.141592653589793) q[1];
cx q[0],q[1];
cx q[0],q[13];
ry(0.9999999999999996) q[0];
cx q[2],q[1];
rz(pi/2) q[1];
swap q[2],q[1];
rz(1.0) q[13];
cx q[0],q[13];
sx q[0];
rz(pi/2) q[0];
cx q[12],q[13];
rz(pi/2) q[12];
ry(0.9999999999999997) q[12];
rz(1.0) q[13];
x q[13];
cx q[12],q[13];
ry(-pi/2) q[13];
rz(-pi/2) q[13];
rz(pi/2) q[15];
cx q[14],q[15];
swap q[14],q[13];
cx q[13],q[0];
rz(pi/2) q[0];
swap q[13],q[12];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
cx q[1],q[0];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
ry(-pi/2) q[12];
rz(-pi) q[12];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
cx q[1],q[0];
rz(pi/2) q[0];
ry(-0.24999999999999972) q[1];
cx q[1],q[2];
ry(0.24999999999999972) q[1];
rz(-pi/2) q[1];
rz(pi/2) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
cx q[1],q[2];
sx q[1];
swap q[2],q[1];
rz(pi/2) q[12];
swap q[12],q[13];
cx q[12],q[1];
rz(4.141592653589793) q[1];
sx q[1];
ry(0.9999999999999996) q[12];
cx q[12],q[1];
sx q[12];
rz(pi/2) q[12];
cx q[13],q[0];
cx q[1],q[0];
rz(pi/2) q[0];
swap q[14],q[13];
cx q[13],q[12];
rz(-2.141592653589793) q[12];
rx(-pi/2) q[12];
ry(0.9999999999999998) q[13];
rz(-pi/2) q[13];
cx q[13],q[12];
swap q[12],q[1];
cx q[1],q[2];
rz(pi/2) q[2];
cx q[12],q[1];
ry(-pi/2) q[1];
rz(-pi) q[1];
ry(0.24999999999999972) q[12];
swap q[12],q[1];
cx q[1],q[0];
ry(-0.2500000000000004) q[1];
cx q[1],q[2];
ry(0.24999999999999972) q[1];
cx q[1],q[0];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
cx q[1],q[12];
ry(0.24999999999999972) q[1];
cx q[1],q[0];
ry(-0.2500000000000004) q[1];
cx q[1],q[2];
rz(-pi) q[1];
ry(-0.24999999999999972) q[1];
cx q[1],q[0];
rz(pi/2) q[0];
ry(0.24999999999999972) q[1];
rz(-pi/2) q[1];
rz(pi/2) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
cx q[1],q[0];
cx q[7],q[0];
rz(pi/2) q[0];
swap q[7],q[0];
rz(pi/2) q[12];
swap q[12],q[1];
cx q[1],q[2];
sx q[13];
rz(-pi/2) q[13];
cx q[13],q[14];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
swap q[7],q[0];
ry(-0.24999999999999994) q[13];
ry(-pi/2) q[14];
rz(-pi) q[14];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[0];
swap q[7],q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
sx q[0];
swap q[7],q[0];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
swap q[7],q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(2.8915926535897927) q[13];
rz(pi/2) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
cx q[0],q[7];
sx q[13];
rz(2.570796326794896) q[13];
ry(-pi/2) q[14];
rz(-pi) q[14];
cx q[13],q[14];
sx q[13];
rz(pi) q[13];
rz(11.566370614359174) q[14];
sx q[14];
cx q[13],q[14];
swap q[14],q[13];
cx q[12],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[15],q[14];
swap q[14],q[13];
cx q[0],q[13];
swap q[1],q[0];
cx q[0],q[7];
cx q[0],q[1];
ry(0.24999999999999972) q[0];
ry(-pi/2) q[1];
rz(-pi) q[1];
rz(pi/2) q[7];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(pi/2) q[13];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.24999999999999972) q[0];
rz(-pi) q[0];
cx q[0],q[1];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
cx q[0],q[7];
ry(-0.2500000000000004) q[0];
rz(-pi/2) q[0];
rz(pi/2) q[1];
sx q[1];
cx q[0],q[1];
rz(pi/2) q[7];
cx q[0],q[7];
sx q[0];
rz(pi/2) q[13];
swap q[13],q[12];
cx q[1],q[12];
sx q[1];
swap q[1],q[0];
cx q[0],q[7];
rz(-pi/2) q[0];
ry(-1.0000000000000004) q[0];
rz(4.141592653589793) q[7];
x q[7];
cx q[0],q[7];
cx q[0],q[1];
ry(-2.141592653589793) q[0];
rz(-pi/2) q[0];
rz(1.0) q[1];
rx(-pi/2) q[1];
cx q[0],q[1];
sx q[0];
rz(pi/2) q[0];
cx q[0],q[7];
rz(pi/2) q[7];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
swap q[7],q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
cx q[13],q[0];
swap q[7],q[0];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
sx q[0];
swap q[7],q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
swap q[7],q[0];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
rz(-pi/2) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
cx q[0],q[7];
ry(-pi/2) q[14];
rz(-pi) q[14];
cx q[13],q[14];
rz(pi/2) q[14];
sx q[14];
swap q[14],q[13];
swap q[12],q[13];
swap q[12],q[1];
cx q[1],q[2];
rz(pi/2) q[1];
ry(0.9999999999999997) q[1];
rz(4.141592653589793) q[2];
sx q[2];
cx q[1],q[2];
sx q[1];
rz(pi/2) q[1];
swap q[15],q[14];
cx q[14],q[13];
rz(7.283185307179586) q[13];
ry(-2.141592653589793) q[14];
rz(-pi/2) q[14];
cx q[14],q[13];
ry(-pi/2) q[13];
rz(-pi/2) q[13];
swap q[12],q[13];
cx q[12],q[1];
rz(1.0) q[1];
sx q[1];
ry(-2.141592653589793) q[12];
rz(-pi/2) q[12];
cx q[12],q[1];
cx q[1],q[2];
ry(-pi/2) q[2];
rz(-pi) q[2];
sx q[12];
rz(pi/2) q[12];
sx q[14];
rz(pi/2) q[14];
cx q[13],q[14];
swap q[13],q[12];
cx q[1],q[12];
rz(-pi) q[1];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.2500000000000004) q[1];
ry(-pi/2) q[12];
rz(-pi) q[12];
ry(-pi/2) q[14];
rz(-pi) q[14];
swap q[14],q[13];
swap q[13],q[0];
cx q[1],q[0];
rz(-pi) q[1];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
cx q[1],q[12];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.2500000000000004) q[1];
cx q[1],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
rz(-pi) q[1];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.24999999999999956) q[1];
rz(pi/2) q[1];
ry(-pi/2) q[2];
rz(-pi) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
cx q[1],q[2];
rz(pi/2) q[12];
swap q[1],q[12];
cx q[1],q[0];
cx q[0],q[13];
swap q[2],q[1];
swap q[1],q[0];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[13],q[12];
ry(-pi/2) q[12];
rz(-pi) q[12];
swap q[15],q[14];
swap q[14],q[13];
cx q[0],q[13];
cx q[0],q[1];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
ry(-pi/2) q[1];
rz(-pi) q[1];
ry(-pi/2) q[13];
rz(-pi) q[13];
cx q[0],q[13];
ry(-0.24999999999999972) q[0];
swap q[15],q[14];
swap q[14],q[13];
cx q[0],q[13];
ry(-0.24999999999999994) q[0];
swap q[14],q[13];
cx q[0],q[13];
ry(-0.24999999999999972) q[0];
cx q[0],q[1];
ry(-0.24999999999999994) q[0];
cx q[0],q[13];
ry(-0.24999999999999972) q[0];
rz(pi/2) q[1];
sx q[1];
swap q[14],q[13];
cx q[0],q[13];
ry(-0.24999999999999994) q[0];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[0],q[13];
ry(-0.2500000000000004) q[0];
cx q[0],q[1];
rz(-pi/2) q[1];
ry(-pi/2) q[13];
rz(-pi) q[13];
cx q[0],q[13];
sx q[0];
swap q[7],q[0];
rz(pi/2) q[13];
sx q[13];
cx q[13],q[0];
rz(1.0) q[0];
rz(-pi/2) q[13];
ry(-0.9999999999999997) q[13];
cx q[13],q[0];
cx q[7],q[0];
rz(1.0) q[0];
rx(-pi/2) q[0];
rz(-pi) q[7];
rx(-1.0000000000000004) q[7];
cx q[7],q[0];
sx q[7];
rz(pi/2) q[7];
sx q[13];
rz(pi/2) q[13];
swap q[14],q[13];
swap q[13],q[12];
cx q[1],q[12];
cx q[1],q[2];
ry(-pi/2) q[2];
rz(-pi) q[2];
rz(pi/2) q[12];
sx q[12];
swap q[12],q[13];
cx q[13],q[14];
rx(0.9999999999999998) q[13];
rz(1.0) q[14];
rx(-pi/2) q[14];
cx q[13],q[14];
sx q[13];
rz(pi/2) q[13];
swap q[15],q[14];
swap q[14],q[13];
swap q[13],q[12];
cx q[1],q[12];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
swap q[1],q[0];
cx q[0],q[13];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
swap q[0],q[1];
cx q[1],q[2];
ry(-0.2500000000000004) q[1];
ry(-pi/2) q[12];
rz(-pi) q[12];
cx q[1],q[12];
rz(-pi) q[1];
ry(-0.24999999999999994) q[1];
cx q[1],q[2];
ry(-0.24999999999999972) q[1];
rz(-pi) q[1];
swap q[1],q[0];
cx q[0],q[13];
rz(-pi) q[0];
ry(-0.24999999999999994) q[0];
swap q[0],q[1];
cx q[1],q[2];
ry(2.891592653589793) q[1];
rz(pi/2) q[2];
rz(pi/2) q[12];
sx q[12];
cx q[1],q[12];
sx q[1];
cx q[2],q[1];
rz(-pi/2) q[1];
ry(-0.5707963267948979) q[1];
ry(0.9999999999999998) q[2];
rz(-pi/2) q[2];
cx q[2],q[1];
cx q[1],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
sx q[2];
rz(pi/2) q[2];
swap q[7],q[0];
rz(pi/2) q[12];
ry(-pi/2) q[13];
rz(-pi) q[13];
cx q[12],q[13];
cx q[13],q[14];
swap q[0],q[13];
cx q[13],q[12];
cx q[0],q[13];
ry(0.24999999999999972) q[0];
ry(-pi/2) q[12];
rz(-pi) q[12];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[0],q[13];
ry(-pi/2) q[14];
rz(-pi) q[14];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
rz(-pi) q[13];
cx q[13],q[12];
ry(0.24999999999999972) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
sx q[0];
ry(0.24999999999999972) q[13];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
rz(-pi) q[13];
cx q[13],q[12];
ry(-pi/2) q[12];
rz(-pi) q[12];
ry(0.24999999999999972) q[13];
cx q[13],q[14];
ry(-0.2500000000000004) q[13];
rz(-pi/2) q[13];
cx q[13],q[0];
rz(pi/2) q[0];
ry(-pi/2) q[14];
rz(-pi) q[14];
cx q[13],q[14];
swap q[0],q[13];
swap q[7],q[0];
cx q[13],q[12];
swap q[12],q[1];
cx q[1],q[2];
ry(-pi/2) q[2];
rz(-pi) q[2];
cx q[12],q[1];
ry(-pi/2) q[1];
rz(-pi) q[1];
swap q[2],q[1];
rz(-pi) q[12];
ry(-0.24999999999999994) q[12];
cx q[13],q[14];
swap q[0],q[13];
cx q[12],q[13];
ry(-0.24999999999999972) q[12];
cx q[12],q[1];
swap q[2],q[1];
ry(-0.24999999999999994) q[12];
cx q[12],q[13];
ry(-0.24999999999999972) q[12];
cx q[12],q[1];
rz(pi/2) q[1];
sx q[1];
swap q[2],q[1];
ry(-0.24999999999999994) q[12];
cx q[12],q[13];
ry(-0.24999999999999972) q[12];
cx q[12],q[1];
ry(-pi/2) q[1];
rz(-pi) q[1];
swap q[2],q[1];
ry(-0.24999999999999994) q[12];
cx q[12],q[13];
ry(-0.24999999999999956) q[12];
rz(pi/2) q[12];
cx q[12],q[1];
rz(pi/2) q[1];
cx q[1],q[2];
ry(-pi/2) q[13];
rz(-pi) q[13];
cx q[12],q[13];
ry(-pi/2) q[14];
rz(-pi) q[14];
swap q[15],q[14];
cx q[14],q[13];
ry(-pi/2) q[13];
rz(-pi) q[13];
swap q[14],q[13];
cx q[13],q[0];
ry(-pi/2) q[0];
rz(-pi) q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
rz(-pi) q[13];
swap q[13],q[14];
cx q[14],q[15];
rz(-pi) q[14];
ry(-0.24999999999999994) q[14];
cx q[14],q[13];
ry(-0.24999999999999972) q[14];
rz(-pi) q[14];
swap q[14],q[13];
cx q[13],q[0];
rz(pi/2) q[0];
sx q[0];
rz(-pi) q[13];
ry(-0.24999999999999994) q[13];
cx q[13],q[14];
ry(-0.24999999999999972) q[13];
swap q[15],q[14];
cx q[13],q[14];
ry(-0.24999999999999994) q[13];
ry(-pi/2) q[14];
rz(-pi) q[14];
swap q[13],q[14];
swap q[0],q[13];
cx q[14],q[15];
ry(-0.24999999999999956) q[14];
rz(pi/2) q[14];
cx q[14],q[13];
rz(pi/2) q[13];
cx q[13],q[0];
ry(-pi/2) q[15];
rz(-pi) q[15];
cx q[14],q[15];
