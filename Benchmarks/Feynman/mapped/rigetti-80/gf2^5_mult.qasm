OPENQASM 2.0;
include "qelib1.inc";
qreg q[80];
rz(pi/4) q[9];
rz(pi/4) q[10];
ry(-pi/2) q[16];
rz(-pi) q[16];
rz(15*pi/4) q[17];
rz(pi/4) q[18];
rz(3*pi/4) q[19];
ry(-pi/2) q[20];
rz(-pi) q[20];
cx q[20],q[19];
cx q[9],q[20];
rz(15*pi/4) q[19];
rz(15*pi/4) q[20];
swap q[19],q[20];
cx q[9],q[20];
rz(pi/4) q[20];
swap q[19],q[20];
cx q[9],q[20];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[19],q[20];
cx q[9],q[20];
swap q[10],q[9];
cx q[19],q[18];
rz(15*pi/4) q[18];
swap q[19],q[20];
cx q[9],q[20];
swap q[18],q[19];
rz(15*pi/4) q[20];
swap q[9],q[20];
cx q[20],q[19];
rz(pi/4) q[19];
cx q[20],q[9];
swap q[19],q[20];
cx q[9],q[20];
rz(15*pi/4) q[20];
cx q[19],q[20];
rz(pi/4) q[21];
rz(15*pi/4) q[22];
rz(5*pi/4) q[23];
rz(15*pi/4) q[28];
rz(pi/4) q[29];
ry(-pi/2) q[62];
rz(-pi) q[62];
ry(-pi/2) q[63];
rz(-pi) q[63];
cx q[63],q[18];
rz(15*pi/4) q[18];
swap q[63],q[62];
cx q[19],q[62];
cx q[19],q[18];
rz(pi/4) q[18];
rz(15*pi/4) q[62];
cx q[19],q[62];
swap q[62],q[19];
cx q[19],q[18];
rz(15*pi/4) q[18];
swap q[18],q[63];
rz(pi/4) q[19];
cx q[19],q[20];
rz(pi/4) q[20];
swap q[9],q[20];
cx q[20],q[21];
rz(pi/4) q[21];
swap q[22],q[21];
cx q[21],q[20];
rz(pi/4) q[20];
cx q[21],q[22];
cx q[21],q[20];
swap q[20],q[21];
rz(15*pi/4) q[22];
cx q[21],q[22];
rz(pi/4) q[22];
swap q[21],q[22];
cx q[20],q[21];
cx q[20],q[19];
rz(pi/4) q[19];
cx q[20],q[9];
rz(15*pi/4) q[9];
cx q[20],q[19];
swap q[19],q[20];
cx q[20],q[9];
rz(pi/4) q[9];
cx q[20],q[21];
swap q[9],q[20];
cx q[19],q[20];
rz(15*pi/4) q[21];
swap q[22],q[23];
swap q[23],q[16];
cx q[16],q[17];
rz(pi/4) q[17];
swap q[28],q[17];
cx q[17],q[16];
rz(pi/4) q[16];
cx q[17],q[28];
cx q[17],q[16];
rz(pi/2) q[16];
rz(15*pi/4) q[28];
cx q[62],q[63];
cx q[18],q[63];
cx q[19],q[18];
rz(15*pi/4) q[18];
swap q[19],q[18];
rz(15*pi/4) q[63];
cx q[18],q[63];
cx q[18],q[19];
rz(pi/4) q[63];
swap q[63],q[18];
cx q[19],q[18];
rz(15*pi/4) q[18];
cx q[19],q[20];
rz(pi/4) q[20];
cx q[63],q[18];
swap q[18],q[17];
swap q[16],q[17];
cx q[17],q[28];
sx q[17];
rz(pi/2) q[17];
cx q[23],q[16];
rz(pi/4) q[16];
swap q[23],q[16];
rz(pi/4) q[28];
swap q[28],q[17];
cx q[18],q[17];
swap q[18],q[19];
swap q[19],q[20];
cx q[20],q[9];
rz(15*pi/4) q[9];
x q[9];
cx q[20],q[21];
cx q[20],q[9];
rz(pi/2) q[9];
rz(pi/4) q[21];
x q[21];
swap q[21],q[8];
cx q[9],q[8];
rz(15*pi/4) q[8];
sx q[9];
swap q[8],q[9];
cx q[20],q[9];
swap q[8],q[9];
swap q[20],q[19];
cx q[19],q[18];
rz(pi/4) q[18];
cx q[19],q[20];
cx q[19],q[18];
rz(pi/2) q[18];
swap q[18],q[19];
rz(15*pi/4) q[20];
cx q[19],q[20];
sx q[19];
rz(pi/2) q[19];
rz(pi/4) q[20];
swap q[19],q[20];
cx q[18],q[19];
swap q[18],q[17];
cx q[17],q[16];
rz(pi/4) q[16];
swap q[17],q[16];
cx q[16],q[23];
cx q[16],q[17];
swap q[17],q[16];
cx q[20],q[21];
swap q[20],q[19];
swap q[19],q[18];
ry(-pi/2) q[21];
rz(-pi) q[21];
rz(15*pi/4) q[23];
cx q[16],q[23];
rz(3*pi/4) q[16];
ry(pi/2) q[16];
swap q[16],q[17];
cx q[17],q[28];
swap q[17],q[18];
swap q[18],q[19];
rz(pi/4) q[23];
cx q[16],q[23];
swap q[23],q[22];
cx q[21],q[22];
rz(15*pi/4) q[22];
swap q[23],q[22];
cx q[22],q[21];
rz(15*pi/4) q[21];
cx q[22],q[23];
cx q[22],q[21];
rz(pi/4) q[23];
swap q[23],q[22];
cx q[21],q[22];
rz(3*pi/4) q[21];
cx q[21],q[20];
rz(15*pi/4) q[20];
swap q[21],q[20];
swap q[9],q[20];
cx q[10],q[9];
rz(15*pi/4) q[9];
cx q[20],q[19];
ry(-pi/2) q[19];
rz(-pi) q[19];
sx q[20];
rz(pi/2) q[20];
swap q[21],q[20];
swap q[20],q[9];
cx q[10],q[9];
rz(pi/4) q[9];
swap q[20],q[9];
cx q[10],q[9];
cx q[9],q[20];
cx q[9],q[8];
rz(pi/4) q[8];
rz(15*pi/4) q[20];
swap q[9],q[20];
cx q[10],q[9];
swap q[19],q[20];
cx q[20],q[9];
rz(15*pi/4) q[9];
swap q[8],q[9];
rz(15*pi/4) q[22];
cx q[23],q[22];
swap q[23],q[22];
swap q[22],q[21];
cx q[21],q[20];
rz(15*pi/4) q[20];
cx q[21],q[8];
rz(pi/4) q[8];
cx q[21],q[20];
swap q[9],q[20];
cx q[9],q[8];
rz(15*pi/4) q[8];
cx q[21],q[8];
rz(pi/2) q[28];
cx q[28],q[17];
ry(-pi/2) q[17];
rz(-pi) q[17];
sx q[28];
rz(pi/2) q[28];
swap q[29],q[28];
cx q[62],q[19];
rz(pi/4) q[19];
swap q[62],q[19];
cx q[19],q[20];
cx q[19],q[62];
rz(15*pi/4) q[20];
swap q[62],q[19];
cx q[19],q[20];
cx q[19],q[18];
rz(15*pi/4) q[18];
swap q[19],q[62];
rz(pi/4) q[20];
cx q[19],q[20];
cx q[9],q[20];
cx q[10],q[9];
rz(15*pi/4) q[9];
rz(15*pi/4) q[20];
swap q[20],q[9];
cx q[10],q[9];
rz(pi/4) q[9];
swap q[10],q[9];
cx q[9],q[20];
swap q[10],q[9];
cx q[20],q[9];
rz(15*pi/4) q[9];
cx q[10],q[9];
cx q[63],q[62];
rz(15*pi/4) q[62];
cx q[63],q[18];
rz(pi/4) q[18];
cx q[63],q[62];
swap q[62],q[63];
cx q[63],q[18];
rz(15*pi/4) q[18];
swap q[18],q[63];
swap q[18],q[17];
cx q[17],q[28];
cx q[16],q[17];
rz(15*pi/4) q[17];
swap q[18],q[19];
swap q[19],q[20];
cx q[20],q[9];
rz(15*pi/4) q[9];
swap q[9],q[8];
cx q[21],q[20];
rz(15*pi/4) q[20];
cx q[21],q[8];
rz(pi/4) q[8];
swap q[8],q[9];
cx q[21],q[20];
cx q[20],q[9];
rz(15*pi/4) q[9];
rz(pi/4) q[20];
rz(15*pi/4) q[28];
swap q[28],q[17];
cx q[16],q[17];
swap q[16],q[29];
swap q[16],q[23];
rz(pi/4) q[17];
cx q[29],q[28];
rz(pi/2) q[28];
cx q[28],q[17];
rz(15*pi/4) q[17];
sx q[28];
rz(pi/2) q[28];
swap q[29],q[28];
cx q[28],q[17];
cx q[62],q[63];
swap q[63],q[62];
cx q[19],q[62];
cx q[18],q[19];
rz(pi/4) q[19];
swap q[18],q[19];
rz(pi/4) q[62];
cx q[19],q[62];
cx q[19],q[18];
rz(15*pi/4) q[62];
swap q[62],q[19];
cx q[18],q[19];
cx q[18],q[17];
rz(pi/4) q[17];
rz(pi/4) q[19];
cx q[62],q[19];
cx q[20],q[19];
swap q[9],q[20];
cx q[10],q[9];
rz(pi/4) q[9];
rz(pi/4) q[19];
cx q[21],q[20];
swap q[19],q[20];
swap q[20],q[9];
cx q[10],q[9];
rz(15*pi/4) q[9];
swap q[20],q[9];
cx q[10],q[9];
cx q[9],q[20];
rz(pi/4) q[20];
swap q[9],q[20];
cx q[10],q[9];
swap q[9],q[8];
swap q[10],q[9];
swap q[22],q[21];
cx q[21],q[8];
rz(15*pi/4) q[8];
cx q[22],q[21];
rz(15*pi/4) q[21];
swap q[8],q[21];
cx q[22],q[21];
rz(pi/4) q[21];
swap q[22],q[21];
cx q[21],q[8];
swap q[22],q[21];
cx q[8],q[21];
rz(15*pi/4) q[21];
cx q[22],q[21];
swap q[23],q[22];
cx q[63],q[18];
rz(pi/4) q[18];
swap q[17],q[18];
cx q[63],q[18];
rz(15*pi/4) q[18];
swap q[63],q[18];
cx q[18],q[17];
rz(pi/2) q[17];
swap q[63],q[18];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[17];
rz(pi/4) q[18];
cx q[63],q[18];
swap q[18],q[19];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[20],q[19];
cx q[62],q[19];
rz(15*pi/4) q[19];
swap q[62],q[19];
cx q[19],q[20];
cx q[19],q[62];
rz(pi/4) q[20];
rz(pi/2) q[62];
swap q[62],q[19];
cx q[19],q[20];
sx q[19];
rz(pi/2) q[19];
rz(15*pi/4) q[20];
swap q[62],q[19];
cx q[19],q[20];
swap q[20],q[21];
cx q[8],q[21];
cx q[9],q[8];
rz(pi/4) q[8];
swap q[9],q[8];
rz(pi/4) q[21];
cx q[8],q[21];
cx q[8],q[9];
rz(pi/2) q[9];
swap q[9],q[20];
rz(15*pi/4) q[21];
cx q[20],q[21];
sx q[20];
rz(pi/2) q[20];
rz(pi/4) q[21];
cx q[8],q[21];
cx q[22],q[21];
rz(15*pi/4) q[21];
cx q[23],q[22];
rz(15*pi/4) q[22];
swap q[23],q[22];
cx q[22],q[21];
rz(pi/4) q[21];
cx q[22],q[23];
swap q[21],q[22];
cx q[23],q[22];
rz(15*pi/4) q[22];
cx q[21],q[22];
rz(-3*pi/4) q[23];
ry(pi/2) q[23];
