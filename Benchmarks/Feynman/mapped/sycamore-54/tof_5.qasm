OPENQASM 2.0;
include "qelib1.inc";
qreg q[54];
ry(-pi/2) q[1];
rz(-pi) q[1];
cx q[1],q[6];
rz(15*pi/4) q[6];
ry(-pi/2) q[7];
rz(-pi) q[7];
cx q[7],q[14];
rz(15*pi/4) q[14];
ry(-pi/2) q[18];
rz(-pi) q[18];
cx q[18],q[12];
rz(15*pi/4) q[12];
cx q[13],q[18];
rz(15*pi/4) q[18];
swap q[13],q[18];
cx q[18],q[12];
rz(pi/4) q[12];
cx q[18],q[13];
swap q[13],q[6];
cx q[6],q[12];
rz(-pi/4) q[6];
rx(-pi/2) q[6];
cx q[6],q[1];
rz(15*pi/4) q[1];
cx q[6],q[13];
cx q[6],q[1];
rz(pi/4) q[13];
swap q[13],q[6];
cx q[1],q[6];
rz(-pi/4) q[1];
rx(-pi/2) q[1];
cx q[1],q[7];
rz(15*pi/4) q[7];
cx q[13],q[6];
swap q[14],q[7];
cx q[1],q[7];
rz(pi/4) q[7];
swap q[1],q[7];
cx q[7],q[14];
swap q[1],q[7];
cx q[14],q[7];
cx q[1],q[7];
rz(3*pi/4) q[14];
sx q[14];
rz(5*pi/4) q[14];
cx q[18],q[12];
rz(pi/4) q[19];
ry(-pi/2) q[26];
rz(-pi) q[26];
cx q[26],q[19];
rz(15*pi/4) q[19];
swap q[26],q[20];
cx q[14],q[20];
cx q[14],q[19];
rz(pi/4) q[19];
rz(15*pi/4) q[20];
cx q[14],q[20];
swap q[20],q[26];
cx q[26],q[19];
rz(15*pi/4) q[19];
cx q[14],q[19];
sx q[14];
rz(pi/2) q[14];
cx q[14],q[7];
rz(pi/4) q[7];
swap q[1],q[7];
cx q[7],q[14];
cx q[7],q[1];
rz(15*pi/4) q[1];
rz(pi/4) q[14];
cx q[7],q[14];
swap q[1],q[7];
cx q[14],q[7];
cx q[1],q[7];
sx q[1];
rz(pi/2) q[1];
cx q[1],q[6];
rz(pi/4) q[6];
swap q[13],q[6];
cx q[6],q[1];
rz(pi/4) q[1];
cx q[6],q[13];
cx q[6],q[1];
swap q[1],q[7];
rz(15*pi/4) q[13];
cx q[7],q[13];
cx q[6],q[13];
sx q[6];
rz(pi/2) q[6];
cx q[6],q[12];
rz(3*pi/4) q[7];
ry(pi/2) q[7];
rz(pi/4) q[12];
rz(3*pi/4) q[14];
ry(pi/2) q[14];
swap q[18],q[12];
cx q[12],q[6];
rz(pi/4) q[6];
cx q[12],q[18];
cx q[12],q[6];
rz(15*pi/4) q[18];
swap q[18],q[12];
cx q[6],q[12];
rz(3*pi/4) q[6];
ry(pi/2) q[6];
cx q[18],q[12];
rz(-3*pi/4) q[26];
ry(pi/2) q[26];
