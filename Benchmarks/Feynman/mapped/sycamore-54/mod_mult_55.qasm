OPENQASM 2.0;
include "qelib1.inc";
qreg q[54];
rz(pi) q[4];
rz(7*pi/4) q[5];
rz(pi) q[9];
ry(pi/2) q[11];
ry(-pi/2) q[16];
rz(-pi) q[16];
rz(pi/4) q[17];
x q[17];
cx q[11],q[17];
cx q[5],q[11];
rz(15*pi/4) q[11];
x q[11];
swap q[5],q[11];
rz(15*pi/4) q[17];
x q[17];
cx q[11],q[17];
cx q[11],q[5];
swap q[5],q[10];
rz(pi/4) q[17];
cx q[10],q[17];
rz(3*pi/4) q[10];
sx q[10];
rz(3*pi/4) q[10];
rz(13*pi/4) q[17];
cx q[11],q[17];
cx q[16],q[21];
cx q[10],q[16];
rz(15*pi/4) q[16];
rz(15*pi/4) q[21];
swap q[21],q[16];
cx q[10],q[16];
rz(pi/4) q[16];
swap q[21],q[16];
cx q[10],q[16];
cx q[16],q[21];
rz(-pi/4) q[16];
rx(-pi/2) q[16];
swap q[10],q[16];
cx q[10],q[4];
rz(pi/2) q[4];
rz(15*pi/4) q[21];
x q[21];
cx q[16],q[21];
ry(-pi/2) q[22];
rz(-pi) q[22];
cx q[22],q[17];
rz(15*pi/4) q[17];
swap q[11],q[17];
cx q[17],q[22];
cx q[17],q[11];
rz(pi/4) q[11];
rz(15*pi/4) q[22];
cx q[17],q[22];
swap q[11],q[17];
cx q[22],q[17];
cx q[11],q[17];
rz(3*pi/4) q[22];
sx q[22];
rz(3*pi/4) q[22];
cx q[22],q[16];
swap q[10],q[16];
cx q[16],q[9];
ry(-pi/2) q[9];
rz(-pi) q[9];
sx q[16];
rz(pi/2) q[16];
cx q[16],q[21];
rz(15*pi/4) q[21];
cx q[22],q[16];
rz(15*pi/4) q[16];
swap q[21],q[16];
cx q[22],q[16];
rz(pi/4) q[16];
swap q[21],q[28];
cx q[22],q[28];
swap q[28],q[21];
cx q[21],q[16];
rz(15*pi/4) q[16];
x q[16];
rz(-3*pi/4) q[21];
ry(pi/2) q[21];
swap q[21],q[15];
cx q[15],q[8];
cx q[22],q[16];
cx q[9],q[16];
swap q[4],q[9];
cx q[10],q[4];
rz(pi/4) q[4];
x q[4];
rz(pi/4) q[16];
x q[16];
cx q[10],q[16];
cx q[10],q[4];
rz(15*pi/4) q[16];
x q[16];
swap q[9],q[16];
cx q[4],q[9];
rz(3*pi/4) q[4];
ry(pi/2) q[4];
swap q[10],q[4];
cx q[4],q[9];
cx q[16],q[22];
sx q[16];
rz(pi/2) q[16];
cx q[16],q[9];
rz(pi/4) q[9];
x q[9];
swap q[4],q[9];
cx q[9],q[16];
cx q[9],q[4];
rz(15*pi/4) q[4];
x q[4];
rz(pi/4) q[16];
x q[16];
cx q[9],q[16];
swap q[4],q[9];
cx q[16],q[9];
cx q[4],q[9];
rz(3*pi/4) q[16];
ry(pi/2) q[16];
ry(-pi/2) q[22];
rz(-pi) q[22];
cx q[22],q[17];
rz(pi/4) q[17];
swap q[11],q[17];
cx q[17],q[22];
cx q[17],q[11];
rz(15*pi/4) q[11];
x q[11];
rz(pi/4) q[22];
cx q[17],q[22];
swap q[11],q[17];
cx q[22],q[17];
cx q[11],q[17];
rz(3*pi/4) q[22];
ry(pi/2) q[22];
cx q[16],q[22];
