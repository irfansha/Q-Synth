OPENQASM 2.0;
include "qelib1.inc";
qreg q[80];
ry(-pi/2) q[0];
rz(-pi) q[0];
rz(3*pi/4) q[1];
cx q[0],q[13];
cx q[1],q[0];
rz(15*pi/4) q[0];
swap q[1],q[0];
cx q[0],q[13];
cx q[0],q[1];
swap q[1],q[12];
rz(pi/4) q[13];
cx q[12],q[13];
rz(15*pi/4) q[13];
cx q[0],q[13];
sx q[0];
rz(pi/2) q[0];
cx q[0],q[7];
rz(15*pi/4) q[7];
swap q[6],q[7];
cx q[7],q[0];
rz(15*pi/4) q[0];
cx q[7],q[6];
rz(pi/4) q[6];
cx q[7],q[0];
swap q[6],q[7];
cx q[0],q[7];
rz(3*pi/4) q[0];
sx q[0];
rz(3*pi/4) q[0];
cx q[6],q[7];
cx q[12],q[13];
swap q[12],q[1];
cx q[0],q[1];
cx q[0],q[13];
rz(pi/4) q[1];
cx q[0],q[1];
rz(pi/2) q[1];
swap q[1],q[12];
rz(15*pi/4) q[13];
cx q[12],q[13];
sx q[12];
rz(pi/2) q[12];
rz(pi/4) q[13];
cx q[0],q[13];
sx q[0];
rz(pi/2) q[0];
cx q[0],q[7];
rz(pi/4) q[7];
swap q[6],q[7];
cx q[7],q[0];
rz(pi/4) q[0];
cx q[7],q[6];
rz(15*pi/4) q[6];
cx q[7],q[0];
swap q[6],q[7];
cx q[0],q[7];
rz(3*pi/4) q[0];
ry(pi/2) q[0];
cx q[6],q[7];
