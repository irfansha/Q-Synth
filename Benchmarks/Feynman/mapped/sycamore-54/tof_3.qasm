OPENQASM 2.0;
include "qelib1.inc";
qreg q[54];
ry(-pi/2) q[6];
rz(-pi) q[6];
cx q[6],q[1];
rz(15*pi/4) q[1];
ry(-pi/2) q[12];
rz(-pi) q[12];
rz(pi/4) q[13];
swap q[13],q[6];
cx q[7],q[13];
cx q[7],q[1];
rz(pi/4) q[1];
cx q[12],q[6];
rz(15*pi/4) q[6];
rz(15*pi/4) q[13];
cx q[7],q[13];
swap q[13],q[6];
cx q[6],q[1];
rz(3*pi/4) q[6];
sx q[6];
rz(5*pi/4) q[6];
cx q[6],q[12];
cx q[6],q[13];
cx q[7],q[1];
rz(15*pi/4) q[12];
cx q[6],q[12];
rz(pi/4) q[13];
swap q[12],q[18];
cx q[18],q[13];
rz(15*pi/4) q[13];
cx q[6],q[13];
sx q[6];
rz(pi/2) q[6];
cx q[6],q[1];
rz(pi/4) q[1];
swap q[6],q[13];
cx q[7],q[13];
cx q[7],q[1];
rz(15*pi/4) q[1];
rz(pi/4) q[13];
cx q[7],q[13];
swap q[1],q[7];
cx q[13],q[7];
cx q[1],q[7];
rz(3*pi/4) q[13];
ry(pi/2) q[13];
rz(-3*pi/4) q[18];
ry(pi/2) q[18];
