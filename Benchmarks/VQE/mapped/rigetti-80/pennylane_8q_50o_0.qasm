OPENQASM 2.0;
include "qelib1.inc";
qreg q[80];
rz(pi) q[16];
rz(pi) q[17];
cx q[18],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
rz(3*pi/2) q[63];
cx q[63],q[18];
rz(pi/2) q[18];
cx q[18],q[17];
sx q[63];
rz(pi/2) q[63];
cx q[63],q[62];
ry(0.24999999999999972) q[62];
swap q[62],q[19];
ry(-0.2500000000000004) q[63];
swap q[63],q[18];
cx q[18],q[17];
rz(pi/2) q[17];
sx q[17];
ry(-0.2500000000000004) q[18];
swap q[17],q[18];
cx q[18],q[19];
ry(0.24999999999999972) q[19];
swap q[63],q[18];
cx q[18],q[19];
cx q[18],q[17];
rz(-pi) q[17];
ry(-0.24999999999999972) q[17];
swap q[17],q[18];
ry(-0.2500000000000004) q[19];
swap q[19],q[62];
cx q[63],q[62];
ry(2.8915926535897927) q[62];
swap q[62],q[19];
sx q[63];
rz(pi/2) q[63];
cx q[18],q[63];
ry(2.891592653589793) q[18];
rz(-pi/2) q[18];
cx q[18],q[19];
sx q[18];
rz(pi/2) q[18];
cx q[18],q[17];
rz(pi/2) q[17];
swap q[17],q[18];
cx q[19],q[62];
ry(-pi/2) q[62];
rz(-pi) q[62];
ry(-pi/2) q[63];
rz(-pi) q[63];
cx q[18],q[63];
swap q[18],q[17];
cx q[17],q[16];
ry(-pi/2) q[16];
rz(-pi) q[16];
cx q[18],q[17];
rz(pi/2) q[17];
cx q[17],q[16];
sx q[18];
rz(pi/2) q[18];
swap q[18],q[17];
cx q[17],q[28];
ry(-0.2500000000000004) q[17];
cx q[17],q[16];
rz(pi/2) q[16];
sx q[16];
ry(-0.2500000000000004) q[17];
swap q[16],q[17];
ry(0.24999999999999972) q[28];
cx q[17],q[28];
swap q[18],q[17];
ry(0.24999999999999972) q[28];
cx q[17],q[28];
cx q[17],q[16];
rz(-pi) q[16];
ry(-0.24999999999999972) q[16];
swap q[18],q[17];
ry(-0.2500000000000004) q[28];
cx q[17],q[28];
sx q[17];
rz(pi/2) q[17];
cx q[16],q[17];
ry(-0.2500000000000004) q[16];
rz(-pi/2) q[16];
swap q[16],q[29];
ry(-pi/2) q[17];
rz(-pi) q[17];
swap q[18],q[17];
ry(-0.2500000000000004) q[28];
cx q[29],q[28];
sx q[29];
swap q[29],q[28];
cx q[28],q[17];
rz(pi/2) q[17];
cx q[17],q[18];
cx q[16],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
rz(pi/2) q[18];
swap q[18],q[17];
cx q[17],q[16];
rz(pi/2) q[16];
sx q[17];
rz(pi/2) q[17];
swap q[17],q[18];
cx q[16],q[17];
cx q[18],q[63];
ry(-0.2500000000000004) q[18];
cx q[18],q[17];
rz(pi/2) q[17];
sx q[17];
ry(-0.2500000000000004) q[18];
swap q[17],q[18];
swap q[16],q[17];
ry(0.24999999999999972) q[63];
cx q[18],q[63];
ry(0.24999999999999972) q[63];
swap q[63],q[18];
cx q[17],q[18];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
swap q[16],q[17];
ry(-0.2500000000000004) q[18];
cx q[63],q[18];
rz(-pi) q[18];
ry(-2.891592653589793) q[18];
sx q[63];
rz(pi/2) q[63];
swap q[63],q[18];
cx q[17],q[18];
ry(-2.891592653589793) q[17];
rz(-pi/2) q[17];
ry(-pi/2) q[18];
rz(-pi) q[18];
swap q[63],q[18];
cx q[17],q[18];
sx q[17];
cx q[17],q[16];
rz(pi/2) q[16];
swap q[16],q[17];
rz(pi/2) q[18];
sx q[18];
swap q[17],q[18];
cx q[18],q[63];
sx q[18];
cx q[17],q[18];
rz(-pi) q[17];
rx(-1.0000000000000004) q[17];
rz(1.0) q[18];
rx(-pi/2) q[18];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
swap q[19],q[18];
swap q[29],q[16];
swap q[16],q[17];
rz(pi/2) q[63];
cx q[63],q[18];
sx q[63];
rz(pi/2) q[63];
swap q[18],q[63];
cx q[18],q[17];
ry(0.24999999999999972) q[17];
ry(-0.2500000000000004) q[18];
cx q[63],q[62];
swap q[62],q[19];
cx q[18],q[19];
ry(-0.2500000000000004) q[18];
swap q[17],q[18];
rz(pi/2) q[19];
sx q[19];
cx q[19],q[18];
ry(0.24999999999999972) q[18];
cx q[63],q[18];
ry(-0.2500000000000004) q[18];
cx q[19],q[18];
ry(-0.24999999999999972) q[18];
rz(-pi) q[18];
swap q[17],q[18];
sx q[19];
rz(pi/2) q[19];
cx q[63],q[18];
ry(0.24999999999999972) q[18];
cx q[18],q[19];
ry(0.24999999999999972) q[18];
rz(-pi/2) q[18];
cx q[18],q[17];
rz(pi/2) q[17];
sx q[18];
ry(-pi/2) q[19];
rz(-pi) q[19];
cx q[63],q[18];
rz(pi/2) q[18];
cx q[18],q[19];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
ry(-0.2500000000000004) q[17];
rz(pi/2) q[18];
rz(pi/2) q[19];
sx q[63];
rz(pi/2) q[63];
cx q[18],q[63];
swap q[17],q[18];
swap q[16],q[17];
cx q[18],q[63];
ry(-0.2500000000000004) q[18];
swap q[17],q[18];
rz(pi/2) q[63];
sx q[63];
cx q[63],q[18];
ry(0.24999999999999972) q[18];
swap q[18],q[17];
cx q[16],q[17];
ry(-0.2500000000000004) q[17];
swap q[17],q[18];
cx q[16],q[17];
ry(0.24999999999999972) q[17];
cx q[63],q[18];
rz(-pi) q[18];
ry(-2.891592653589793) q[18];
sx q[63];
rz(pi/2) q[63];
swap q[63],q[18];
cx q[17],q[18];
ry(-2.891592653589793) q[17];
rz(-pi/2) q[17];
ry(-pi/2) q[18];
rz(-pi) q[18];
swap q[17],q[18];
swap q[16],q[17];
cx q[18],q[63];
sx q[18];
cx q[18],q[17];
rz(pi/2) q[17];
cx q[17],q[16];
sx q[17];
swap q[16],q[17];
swap q[18],q[63];
cx q[63],q[62];
ry(-pi/2) q[62];
rz(-pi) q[62];
swap q[19],q[62];
cx q[62],q[63];
sx q[62];
rz(pi/2) q[62];
rz(pi/2) q[63];
swap q[18],q[63];
cx q[18],q[19];
cx q[62],q[63];
ry(-0.2500000000000004) q[62];
cx q[62],q[19];
rz(pi/2) q[19];
sx q[19];
ry(-0.2500000000000004) q[62];
swap q[19],q[62];
ry(0.24999999999999972) q[63];
cx q[62],q[63];
ry(0.24999999999999972) q[63];
cx q[18],q[63];
cx q[18],q[19];
rz(-pi) q[19];
ry(-0.24999999999999972) q[19];
ry(-0.2500000000000004) q[63];
cx q[62],q[63];
sx q[62];
rz(pi/2) q[62];
cx q[19],q[62];
ry(-0.2500000000000004) q[19];
rz(-pi/2) q[19];
ry(-pi/2) q[62];
rz(-pi) q[62];
swap q[19],q[62];
ry(-0.2500000000000004) q[63];
cx q[62],q[63];
swap q[18],q[63];
cx q[18],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
sx q[62];
cx q[62],q[63];
sx q[62];
swap q[63],q[18];
cx q[18],q[19];
cx q[18],q[63];
sx q[18];
rz(pi/2) q[18];
swap q[17],q[18];
cx q[17],q[28];
ry(-0.2500000000000004) q[17];
rz(pi/2) q[19];
ry(0.24999999999999972) q[28];
swap q[62],q[19];
rz(pi/2) q[63];
cx q[63],q[18];
cx q[17],q[18];
ry(-0.2500000000000004) q[17];
rz(pi/2) q[18];
sx q[18];
swap q[18],q[17];
cx q[17],q[28];
ry(0.24999999999999972) q[28];
swap q[63],q[18];
swap q[18],q[17];
cx q[17],q[28];
swap q[17],q[18];
cx q[18],q[63];
ry(-0.2500000000000004) q[28];
cx q[17],q[28];
sx q[17];
rz(pi/2) q[17];
swap q[17],q[18];
rz(-pi) q[28];
ry(-2.891592653589793) q[28];
swap q[28],q[17];
ry(0.24999999999999972) q[63];
cx q[63],q[18];
ry(-pi/2) q[18];
rz(-pi) q[18];
swap q[17],q[18];
swap q[28],q[17];
ry(-2.891592653589793) q[63];
rz(-pi/2) q[63];
cx q[63],q[18];
rz(pi/2) q[18];
sx q[18];
sx q[63];
rz(pi/2) q[63];
swap q[63],q[18];
cx q[18],q[17];
rz(pi/2) q[17];
cx q[17],q[28];
swap q[16],q[17];
sx q[18];
cx q[18],q[17];
rz(4.141592653589793) q[17];
sx q[17];
rz(-pi/2) q[18];
ry(-1.0000000000000004) q[18];
cx q[18],q[17];
rz(pi/2) q[17];
cx q[18],q[19];
rz(-pi) q[18];
ry(-0.9999999999999996) q[18];
rz(1.0) q[19];
cx q[18],q[19];
sx q[18];
rz(pi/2) q[18];
cx q[29],q[28];
ry(-pi/2) q[28];
rz(-pi) q[28];
swap q[29],q[28];
cx q[17],q[28];
sx q[17];
rz(pi/2) q[17];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
ry(-0.2500000000000004) q[17];
swap q[17],q[16];
rz(pi/2) q[28];
cx q[28],q[29];
cx q[16],q[29];
ry(-0.2500000000000004) q[16];
rz(pi/2) q[29];
sx q[29];
swap q[29],q[16];
cx q[16],q[17];
ry(0.24999999999999972) q[17];
cx q[28],q[17];
ry(-0.2500000000000004) q[17];
cx q[16],q[17];
sx q[16];
rz(pi/2) q[16];
ry(-0.2500000000000004) q[17];
cx q[28],q[29];
rz(-pi) q[29];
ry(-0.24999999999999972) q[29];
cx q[29],q[16];
ry(-pi/2) q[16];
rz(-pi) q[16];
ry(-0.2500000000000004) q[29];
rz(-pi/2) q[29];
swap q[29],q[28];
cx q[28],q[17];
rz(pi/2) q[17];
sx q[17];
sx q[28];
rz(pi/2) q[28];
cx q[28],q[29];
sx q[28];
swap q[17],q[28];
cx q[17],q[18];
rz(-pi/2) q[17];
ry(-0.9999999999999997) q[17];
rz(1.0) q[18];
rx(-pi/2) q[18];
cx q[17],q[18];
rz(pi/2) q[18];
rz(pi/2) q[29];
cx q[29],q[16];
sx q[29];
cx q[28],q[29];
rz(-pi/2) q[28];
ry(-0.9999999999999997) q[28];
rz(1.0) q[29];
cx q[28],q[29];
swap q[28],q[17];
swap q[29],q[28];
swap q[63],q[18];
swap q[17],q[18];
cx q[17],q[28];
rx(-2.141592653589793) q[17];
cx q[18],q[19];
ry(-1.0000000000000002) q[18];
rz(-pi/2) q[18];
rz(1.0) q[19];
cx q[18],q[19];
sx q[18];
rz(pi/2) q[18];
rz(7.283185307179586) q[28];
cx q[17],q[28];
sx q[17];
rz(pi/2) q[17];
cx q[18],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
ry(-pi/2) q[28];
rz(-pi/2) q[28];
swap q[62],q[63];
swap q[19],q[62];
cx q[63],q[18];
rz(pi/2) q[18];
cx q[18],q[17];
sx q[63];
rz(pi/2) q[63];
swap q[63],q[18];
swap q[18],q[17];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
ry(-0.2500000000000004) q[17];
cx q[17],q[18];
ry(-0.2500000000000004) q[17];
rz(pi/2) q[18];
sx q[18];
swap q[18],q[17];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
swap q[63],q[18];
swap q[18],q[17];
cx q[17],q[16];
ry(-0.2500000000000004) q[16];
swap q[17],q[18];
cx q[17],q[16];
ry(-0.2500000000000004) q[16];
sx q[17];
rz(pi/2) q[17];
cx q[18],q[63];
swap q[17],q[18];
rz(-pi) q[63];
ry(-0.24999999999999972) q[63];
cx q[63],q[18];
ry(-pi/2) q[18];
rz(-pi) q[18];
ry(-0.2500000000000004) q[63];
rz(-pi/2) q[63];
swap q[63],q[18];
swap q[18],q[17];
cx q[17],q[16];
rz(pi/2) q[16];
sx q[16];
sx q[17];
rz(pi/2) q[17];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[18];
cx q[18],q[63];
sx q[18];
swap q[18],q[17];
cx q[28],q[17];
rz(1.0) q[17];
x q[17];
ry(-2.141592653589793) q[28];
rz(-pi/2) q[28];
cx q[28],q[17];
cx q[18],q[17];
rz(1.0) q[17];
sx q[17];
rx(-2.141592653589793) q[18];
cx q[18],q[17];
swap q[16],q[17];
sx q[18];
rz(pi/2) q[18];
sx q[28];
swap q[29],q[16];
rz(pi/2) q[63];
sx q[63];
cx q[63],q[62];
rz(1.0) q[62];
rz(-pi/2) q[63];
ry(-0.9999999999999997) q[63];
cx q[63],q[62];
sx q[63];
rz(pi/2) q[63];
swap q[63],q[18];
cx q[17],q[18];
rz(pi/2) q[17];
ry(0.9999999999999997) q[17];
rz(4.141592653589793) q[18];
sx q[18];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
cx q[16],q[17];
ry(-1.0000000000000002) q[16];
rz(-pi/2) q[16];
rz(1.0) q[17];
rx(-pi/2) q[17];
cx q[16],q[17];
sx q[16];
rz(pi/2) q[16];
swap q[16],q[17];
cx q[18],q[63];
cx q[19],q[18];
rz(pi/2) q[18];
sx q[19];
rz(pi/2) q[19];
ry(-pi/2) q[63];
rz(-pi) q[63];
cx q[18],q[63];
swap q[17],q[18];
cx q[19],q[18];
ry(0.24999999999999972) q[18];
ry(-0.2500000000000004) q[19];
swap q[63],q[18];
cx q[19],q[18];
rz(pi/2) q[18];
sx q[18];
cx q[18],q[63];
swap q[17],q[18];
ry(-0.2500000000000004) q[19];
ry(0.24999999999999972) q[63];
cx q[18],q[63];
cx q[18],q[19];
swap q[17],q[18];
ry(0.24999999999999972) q[19];
ry(-0.2500000000000004) q[63];
cx q[18],q[63];
sx q[18];
rz(pi/2) q[18];
cx q[19],q[18];
ry(-pi/2) q[18];
rz(-pi) q[18];
swap q[17],q[18];
ry(-2.891592653589793) q[19];
rz(-pi/2) q[19];
rx(-pi/2) q[63];
rz(0.25) q[63];
swap q[63],q[62];
cx q[19],q[62];
sx q[19];
rz(pi/2) q[19];
cx q[19],q[18];
cx q[18],q[17];
swap q[17],q[28];
sx q[18];
sx q[19];
cx q[28],q[29];
cx q[17],q[28];
sx q[17];
rz(pi/2) q[17];
rz(pi/2) q[28];
ry(-pi/2) q[29];
rz(-pi) q[29];
cx q[28],q[29];
swap q[29],q[16];
swap q[62],q[63];
cx q[18],q[63];
rz(pi/2) q[18];
ry(0.9999999999999997) q[18];
rz(4.141592653589793) q[63];
sx q[63];
cx q[18],q[63];
sx q[18];
rz(pi/2) q[18];
cx q[19],q[18];
rz(1.0) q[18];
rx(-pi/2) q[18];
rz(-pi/2) q[19];
ry(-0.9999999999999997) q[19];
cx q[19],q[18];
cx q[17],q[18];
ry(-0.2500000000000004) q[17];
cx q[17],q[16];
rz(pi/2) q[16];
sx q[16];
ry(-0.2500000000000004) q[17];
swap q[16],q[17];
ry(0.24999999999999972) q[18];
cx q[17],q[18];
ry(0.24999999999999972) q[18];
swap q[18],q[17];
sx q[19];
rz(pi/2) q[19];
cx q[28],q[17];
ry(-0.2500000000000004) q[17];
cx q[18],q[17];
ry(2.8915926535897927) q[17];
sx q[18];
rz(pi/2) q[18];
swap q[18],q[17];
swap q[28],q[29];
cx q[29],q[16];
rz(-pi) q[16];
ry(-0.24999999999999972) q[16];
cx q[16],q[17];
ry(2.891592653589793) q[16];
rz(-pi/2) q[16];
ry(-pi/2) q[17];
rz(-pi) q[17];
swap q[18],q[17];
cx q[16],q[17];
sx q[16];
cx q[16],q[29];
cx q[17],q[28];
swap q[18],q[17];
ry(-pi/2) q[28];
rz(-pi) q[28];
rz(pi/2) q[29];
swap q[29],q[16];
cx q[16],q[17];
rz(pi/2) q[17];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
swap q[17],q[28];
rz(pi/2) q[18];
cx q[18],q[17];
cx q[28],q[29];
ry(-0.2500000000000004) q[28];
cx q[28],q[17];
rz(pi/2) q[17];
sx q[17];
ry(-0.2500000000000004) q[28];
swap q[17],q[28];
swap q[18],q[17];
ry(0.24999999999999972) q[29];
cx q[28],q[29];
ry(0.24999999999999972) q[29];
swap q[29],q[16];
cx q[17],q[16];
ry(-0.2500000000000004) q[16];
cx q[17],q[18];
swap q[16],q[17];
rz(-pi) q[18];
ry(-0.24999999999999972) q[18];
cx q[28],q[17];
ry(-0.2500000000000004) q[17];
sx q[28];
rz(pi/2) q[28];
swap q[28],q[17];
cx q[18],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
ry(-0.2500000000000004) q[18];
rz(-pi/2) q[18];
swap q[28],q[17];
cx q[18],q[17];
rz(pi/2) q[17];
swap q[16],q[17];
sx q[18];
rz(pi/2) q[18];
cx q[18],q[17];
cx q[17],q[28];
sx q[17];
sx q[18];
swap q[18],q[63];
swap q[18],q[17];
cx q[17],q[28];
cx q[16],q[17];
sx q[16];
rz(pi/2) q[16];
cx q[16],q[29];
ry(-0.2500000000000004) q[16];
rz(pi/2) q[17];
ry(-pi/2) q[28];
rz(-pi) q[28];
cx q[17],q[28];
ry(0.24999999999999972) q[29];
swap q[28],q[29];
cx q[16],q[29];
ry(-0.2500000000000004) q[16];
rz(pi/2) q[29];
sx q[29];
cx q[29],q[28];
ry(0.24999999999999972) q[28];
cx q[17],q[28];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
ry(-0.2500000000000004) q[28];
cx q[29],q[28];
rx(-pi/2) q[28];
rz(0.25) q[28];
sx q[29];
rz(pi/2) q[29];
cx q[16],q[29];
ry(-2.891592653589793) q[16];
rz(-pi/2) q[16];
swap q[16],q[17];
cx q[17],q[28];
sx q[17];
cx q[17],q[16];
sx q[17];
swap q[17],q[28];
cx q[18],q[17];
rz(1.0) q[17];
x q[17];
rz(-pi/2) q[18];
ry(-0.9999999999999997) q[18];
cx q[18],q[17];
rz(pi/2) q[17];
sx q[17];
ry(-pi/2) q[29];
rz(-pi) q[29];
cx q[16],q[29];
sx q[16];
rz(pi/2) q[29];
sx q[29];
cx q[29],q[28];
rz(7.283185307179586) q[28];
rx(-2.141592653589793) q[29];
cx q[29],q[28];
ry(-pi/2) q[28];
rz(-pi/2) q[28];
swap q[28],q[17];
swap q[17],q[18];
sx q[29];
rz(pi/2) q[29];
cx q[63],q[62];
rz(1.0) q[62];
rz(pi/2) q[63];
ry(0.9999999999999997) q[63];
cx q[63],q[62];
swap q[63],q[62];
cx q[18],q[63];
rz(-pi) q[18];
ry(-0.9999999999999996) q[18];
cx q[62],q[19];
rz(1.0) q[19];
x q[19];
ry(0.9999999999999996) q[62];
cx q[62],q[19];
ry(-pi/2) q[19];
rz(-3*pi/2) q[19];
rz(1.0) q[63];
cx q[18],q[63];
sx q[18];
rz(pi/2) q[18];
swap q[17],q[18];
cx q[16],q[17];
rz(-pi/2) q[16];
ry(-0.9999999999999997) q[16];
rz(1.0) q[17];
rx(-pi/2) q[17];
cx q[16],q[17];
sx q[16];
rz(pi/2) q[16];
swap q[16],q[17];
cx q[18],q[63];
ry(-1.0000000000000002) q[18];
rz(-pi/2) q[18];
swap q[29],q[16];
rz(1.0) q[63];
x q[63];
cx q[18],q[63];
sx q[18];
rz(pi/2) q[18];
swap q[17],q[18];
cx q[19],q[18];
rz(1.0) q[18];
ry(-0.9999999999999996) q[19];
cx q[19],q[18];
sx q[19];
rz(pi/2) q[19];
swap q[18],q[19];
swap q[28],q[17];
cx q[17],q[18];
ry(2.141592653589794) q[17];
rz(-pi/2) q[17];
rz(10.42477796076938) q[18];
sx q[18];
cx q[17],q[18];
sx q[17];
cx q[62],q[19];
rz(11.42477796076938) q[19];
sx q[19];
ry(1.9999999999999996) q[62];
rz(-pi/2) q[62];
cx q[62],q[19];
swap q[19],q[18];
swap q[18],q[17];
cx q[16],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
swap q[18],q[17];
cx q[17],q[16];
rz(pi/2) q[16];
sx q[17];
rz(pi/2) q[17];
cx q[17],q[28];
ry(-0.2500000000000004) q[17];
swap q[18],q[17];
cx q[16],q[17];
cx q[18],q[17];
rz(pi/2) q[17];
sx q[17];
ry(-0.2500000000000004) q[18];
ry(0.24999999999999972) q[28];
cx q[17],q[28];
ry(0.24999999999999972) q[28];
swap q[28],q[29];
cx q[16],q[29];
swap q[16],q[17];
cx q[17],q[18];
rz(-pi) q[18];
ry(-0.24999999999999972) q[18];
ry(-0.2500000000000004) q[29];
cx q[16],q[29];
sx q[16];
rz(pi/2) q[16];
swap q[16],q[17];
cx q[18],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
ry(2.891592653589793) q[18];
rz(-pi/2) q[18];
swap q[18],q[17];
ry(2.8915926535897927) q[29];
swap q[29],q[16];
cx q[17],q[16];
sx q[17];
swap q[29],q[16];
cx q[17],q[16];
sx q[17];
swap q[17],q[18];
cx q[16],q[17];
sx q[16];
sx q[62];
rz(pi/2) q[62];
ry(-pi/2) q[63];
rz(-pi/2) q[63];
cx q[63],q[18];
rz(4.141592653589793) q[18];
sx q[18];
ry(0.9999999999999998) q[63];
rz(-pi/2) q[63];
cx q[63],q[18];
cx q[18],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
sx q[63];
cx q[63],q[18];
rz(pi/2) q[18];
cx q[18],q[17];
swap q[28],q[17];
sx q[63];
rz(pi/2) q[63];
swap q[63],q[18];
cx q[18],q[17];
ry(0.24999999999999972) q[17];
ry(-0.2500000000000004) q[18];
swap q[18],q[17];
cx q[17],q[28];
ry(-0.2500000000000004) q[17];
rz(pi/2) q[28];
sx q[28];
swap q[28],q[17];
cx q[17],q[18];
ry(0.24999999999999972) q[18];
cx q[63],q[18];
ry(-0.2500000000000004) q[18];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
ry(-0.2500000000000004) q[18];
swap q[63],q[18];
swap q[18],q[17];
cx q[17],q[28];
rz(-pi) q[28];
ry(-0.24999999999999972) q[28];
swap q[28],q[17];
cx q[17],q[18];
ry(-0.2500000000000004) q[17];
rz(-pi/2) q[17];
ry(-pi/2) q[18];
rz(-pi) q[18];
swap q[63],q[18];
cx q[17],q[18];
sx q[17];
cx q[17],q[28];
cx q[19],q[18];
ry(-pi/2) q[18];
rz(-pi) q[18];
rz(pi/2) q[28];
swap q[28],q[17];
swap q[63],q[18];
cx q[17],q[18];
swap q[16],q[17];
rz(pi/2) q[18];
cx q[18],q[19];
sx q[18];
rz(pi/2) q[18];
rz(pi/2) q[19];
cx q[29],q[16];
ry(-pi/2) q[16];
rz(-pi) q[16];
swap q[62],q[63];
cx q[18],q[63];
ry(-0.24999999999999972) q[18];
rz(-pi) q[18];
cx q[19],q[62];
swap q[18],q[19];
cx q[19],q[62];
rz(-pi) q[19];
ry(-2.891592653589793) q[19];
ry(-pi/2) q[62];
rz(-pi) q[62];
ry(-2.8915926535897936) q[63];
rz(-pi) q[63];
cx q[62],q[63];
ry(-2.8915926535897936) q[63];
rz(-pi) q[63];
cx q[18],q[63];
cx q[18],q[19];
sx q[18];
rz(-pi) q[19];
ry(-0.24999999999999994) q[19];
rz(-pi) q[63];
ry(-2.891592653589793) q[63];
cx q[62],q[63];
sx q[62];
rz(pi/2) q[62];
cx q[19],q[62];
ry(0.2500000000000004) q[19];
rz(pi/2) q[19];
sx q[63];
rz(6.033185307179586) q[63];
swap q[63],q[18];
cx q[19],q[18];
cx q[17],q[18];
rx(-2.141592653589793) q[17];
rz(7.283185307179586) q[18];
cx q[17],q[18];
sx q[17];
swap q[17],q[28];
rz(pi/2) q[18];
sx q[18];
sx q[19];
swap q[19],q[62];
cx q[28],q[29];
sx q[28];
rz(pi/2) q[28];
cx q[28],q[17];
ry(0.24999999999999972) q[17];
ry(-0.2500000000000004) q[28];
rz(pi/2) q[29];
cx q[29],q[16];
swap q[16],q[17];
cx q[28],q[17];
rz(pi/2) q[17];
sx q[17];
cx q[17],q[16];
ry(0.24999999999999972) q[16];
ry(-0.2500000000000004) q[28];
cx q[29],q[16];
ry(-0.2500000000000004) q[16];
cx q[17],q[16];
rx(-pi/2) q[16];
rz(0.25) q[16];
sx q[17];
rz(pi/2) q[17];
cx q[29],q[28];
ry(0.24999999999999972) q[28];
cx q[28],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
ry(-2.891592653589793) q[28];
rz(-pi/2) q[28];
swap q[28],q[29];
cx q[29],q[16];
sx q[29];
cx q[29],q[28];
cx q[28],q[17];
rz(pi/2) q[17];
swap q[17],q[18];
cx q[17],q[16];
rz(1.0) q[16];
x q[16];
ry(-1.0000000000000002) q[17];
rz(-pi/2) q[17];
cx q[17],q[16];
rz(pi/2) q[16];
sx q[16];
sx q[17];
rz(pi/2) q[17];
sx q[28];
sx q[29];
cx q[28],q[29];
rz(-pi) q[28];
rx(-1.0000000000000004) q[28];
rz(1.0) q[29];
rx(-pi/2) q[29];
cx q[28],q[29];
sx q[28];
rz(pi/2) q[28];
cx q[62],q[63];
ry(-pi/2) q[63];
rz(-pi) q[63];
cx q[18],q[63];
sx q[18];
rz(pi/2) q[18];
cx q[18],q[17];
ry(-2.8915926535897936) q[17];
rz(-pi) q[17];
ry(-0.24999999999999972) q[18];
rz(-pi) q[18];
swap q[19],q[18];
cx q[63],q[18];
cx q[19],q[18];
ry(-pi/2) q[18];
rz(-pi) q[18];
cx q[18],q[17];
ry(0.24999999999999972) q[17];
swap q[17],q[18];
ry(-0.2500000000000004) q[19];
sx q[63];
rz(pi/2) q[63];
cx q[63],q[18];
rz(-pi) q[18];
ry(-2.891592653589793) q[18];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
ry(-0.2500000000000004) q[18];
swap q[19],q[18];
cx q[63],q[18];
rz(-pi) q[18];
ry(-0.24999999999999994) q[18];
cx q[18],q[17];
rz(pi/2) q[17];
ry(0.2500000000000004) q[18];
rz(pi/2) q[18];
cx q[18],q[19];
sx q[18];
cx q[18],q[63];
rz(pi/2) q[63];
swap q[63],q[18];
cx q[18],q[17];
cx q[16],q[17];
ry(-1.0000000000000002) q[16];
rz(-pi/2) q[16];
rz(1.0) q[17];
rx(-pi/2) q[17];
cx q[16],q[17];
sx q[16];
rz(pi/2) q[16];
