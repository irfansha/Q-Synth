OPENQASM 2.0;
include "qelib1.inc";
qreg q[80];
rz(pi) q[8];
rz(pi) q[10];
ry(-pi/2) q[40];
rz(-pi) q[40];
ry(-pi/2) q[48];
rz(-pi) q[48];
ry(-pi/2) q[49];
rz(-pi) q[49];
ry(-pi/2) q[53];
rz(-pi) q[53];
ry(-pi/2) q[56];
rz(-pi) q[56];
cx q[48],q[61];
cx q[55],q[48];
rz(15*pi/4) q[48];
swap q[55],q[48];
rz(15*pi/4) q[61];
cx q[48],q[61];
cx q[48],q[55];
rz(pi/4) q[61];
swap q[61],q[48];
cx q[55],q[48];
rz(15*pi/4) q[48];
rz(15*pi/4) q[55];
cx q[55],q[54];
cx q[10],q[55];
rz(15*pi/4) q[54];
rz(15*pi/4) q[55];
swap q[10],q[55];
cx q[55],q[54];
rz(pi/4) q[54];
cx q[55],q[10];
swap q[54],q[55];
cx q[10],q[55];
cx q[10],q[11];
cx q[9],q[10];
rz(15*pi/4) q[10];
swap q[9],q[10];
rz(15*pi/4) q[11];
cx q[10],q[11];
cx q[10],q[9];
rz(pi/4) q[11];
swap q[11],q[10];
cx q[9],q[10];
cx q[9],q[20];
cx q[8],q[9];
rz(15*pi/4) q[9];
swap q[8],q[9];
rz(15*pi/4) q[10];
cx q[11],q[10];
rz(15*pi/4) q[20];
cx q[9],q[20];
cx q[9],q[8];
swap q[8],q[21];
rz(pi/4) q[20];
cx q[21],q[20];
rz(15*pi/4) q[20];
cx q[9],q[20];
cx q[21],q[8];
rz(15*pi/4) q[8];
cx q[22],q[21];
rz(15*pi/4) q[21];
swap q[22],q[21];
cx q[21],q[8];
rz(pi/4) q[8];
cx q[21],q[22];
swap q[8],q[21];
cx q[22],q[21];
rz(15*pi/4) q[21];
cx q[8],q[21];
rz(15*pi/4) q[55];
cx q[54],q[55];
cx q[61],q[48];
ry(-pi/2) q[62];
rz(-pi) q[62];
ry(-pi/2) q[63];
rz(-pi) q[63];
swap q[56],q[63];
swap q[63],q[62];
swap q[56],q[63];
swap q[62],q[61];
cx q[61],q[48];
rz(15*pi/4) q[48];
swap q[61],q[48];
swap q[48],q[55];
cx q[54],q[55];
rz(3*pi/4) q[55];
swap q[54],q[55];
swap q[55],q[48];
cx q[48],q[61];
swap q[54],q[55];
cx q[48],q[55];
rz(pi/2) q[55];
rz(pi/4) q[61];
swap q[61],q[48];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[55],q[54];
rz(15*pi/4) q[54];
swap q[11],q[54];
cx q[54],q[55];
cx q[54],q[11];
rz(pi/4) q[11];
rz(15*pi/4) q[55];
cx q[54],q[55];
swap q[55],q[10];
cx q[10],q[11];
cx q[10],q[55];
cx q[9],q[10];
rz(15*pi/4) q[10];
swap q[9],q[10];
rz(15*pi/4) q[11];
cx q[54],q[11];
rz(15*pi/4) q[55];
cx q[10],q[55];
cx q[10],q[9];
rz(pi/4) q[55];
swap q[55],q[10];
cx q[9],q[10];
cx q[9],q[20];
cx q[8],q[9];
rz(15*pi/4) q[9];
rz(15*pi/4) q[10];
rz(15*pi/4) q[20];
swap q[20],q[9];
cx q[8],q[9];
rz(pi/4) q[9];
swap q[8],q[9];
cx q[9],q[20];
swap q[20],q[21];
cx q[21],q[8];
rz(15*pi/4) q[8];
cx q[9],q[8];
cx q[21],q[20];
rz(15*pi/4) q[20];
swap q[19],q[20];
swap q[18],q[19];
swap q[20],q[21];
swap q[19],q[20];
cx q[22],q[21];
rz(15*pi/4) q[21];
swap q[20],q[21];
cx q[21],q[22];
cx q[21],q[20];
rz(pi/4) q[20];
rz(15*pi/4) q[22];
cx q[21],q[22];
swap q[20],q[21];
cx q[22],q[21];
rz(15*pi/4) q[21];
cx q[20],q[21];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[18],q[19];
cx q[20],q[19];
rz(pi/4) q[19];
swap q[18],q[19];
cx q[20],q[19];
cx q[19],q[18];
rz(15*pi/4) q[18];
swap q[19],q[20];
cx q[19],q[18];
cx q[20],q[21];
swap q[19],q[20];
rz(15*pi/4) q[21];
cx q[22],q[23];
rz(15*pi/4) q[23];
swap q[16],q[23];
cx q[23],q[22];
rz(15*pi/4) q[22];
cx q[23],q[16];
rz(pi/4) q[16];
cx q[23],q[22];
rz(pi/2) q[22];
swap q[22],q[23];
cx q[23],q[16];
rz(15*pi/4) q[16];
sx q[23];
rz(pi/2) q[23];
swap q[16],q[23];
cx q[22],q[23];
swap q[22],q[21];
cx q[55],q[10];
swap q[54],q[55];
cx q[61],q[48];
swap q[63],q[62];
swap q[56],q[63];
swap q[62],q[61];
cx q[61],q[48];
rz(15*pi/4) q[48];
swap q[61],q[48];
cx q[55],q[48];
rz(15*pi/4) q[48];
swap q[55],q[48];
cx q[48],q[61];
cx q[48],q[55];
rz(pi/4) q[61];
swap q[61],q[48];
cx q[55],q[48];
rz(15*pi/4) q[48];
rz(5*pi/4) q[55];
swap q[55],q[54];
cx q[54],q[11];
rz(15*pi/4) q[11];
swap q[11],q[10];
cx q[55],q[54];
rz(15*pi/4) q[54];
cx q[55],q[10];
rz(pi/4) q[10];
cx q[55],q[54];
swap q[54],q[11];
cx q[11],q[10];
rz(15*pi/4) q[10];
cx q[11],q[54];
rz(15*pi/4) q[54];
cx q[55],q[10];
cx q[61],q[48];
swap q[63],q[62];
swap q[62],q[61];
cx q[61],q[48];
rz(15*pi/4) q[48];
swap q[55],q[48];
cx q[48],q[61];
cx q[48],q[55];
rz(pi/4) q[55];
rz(3*pi/4) q[61];
cx q[48],q[61];
swap q[55],q[48];
cx q[61],q[48];
rz(15*pi/4) q[48];
cx q[55],q[48];
cx q[49],q[48];
rz(15*pi/4) q[48];
swap q[61],q[48];
swap q[48],q[55];
cx q[55],q[10];
rz(15*pi/4) q[10];
swap q[9],q[10];
cx q[10],q[11];
rz(15*pi/4) q[11];
swap q[10],q[11];
cx q[11],q[54];
cx q[11],q[10];
swap q[10],q[11];
rz(pi/4) q[54];
cx q[11],q[54];
swap q[10],q[11];
swap q[10],q[9];
cx q[9],q[8];
rz(15*pi/4) q[8];
cx q[20],q[9];
rz(15*pi/4) q[9];
swap q[20],q[9];
cx q[9],q[8];
rz(pi/4) q[8];
cx q[9],q[20];
swap q[20],q[21];
cx q[20],q[19];
rz(15*pi/4) q[19];
cx q[21],q[8];
rz(15*pi/4) q[8];
cx q[9],q[8];
swap q[20],q[21];
swap q[19],q[20];
cx q[19],q[18];
rz(15*pi/4) q[18];
cx q[21],q[22];
cx q[21],q[20];
rz(pi/2) q[20];
swap q[20],q[21];
rz(pi/4) q[22];
cx q[21],q[22];
sx q[21];
rz(pi/2) q[21];
rz(15*pi/4) q[22];
swap q[22],q[21];
cx q[20],q[21];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[18],q[19];
cx q[20],q[19];
rz(pi/4) q[19];
swap q[18],q[19];
cx q[20],q[19];
rz(pi/2) q[19];
cx q[19],q[18];
rz(15*pi/4) q[18];
sx q[19];
rz(pi/2) q[19];
swap q[18],q[19];
cx q[20],q[19];
rz(15*pi/4) q[54];
cx q[11],q[54];
swap q[11],q[10];
cx q[10],q[55];
cx q[10],q[11];
rz(pi/4) q[11];
rz(15*pi/4) q[55];
cx q[10],q[55];
swap q[55],q[10];
cx q[10],q[11];
rz(15*pi/4) q[11];
swap q[10],q[11];
cx q[11],q[54];
rz(15*pi/4) q[54];
cx q[55],q[10];
swap q[55],q[48];
cx q[48],q[49];
cx q[48],q[61];
rz(15*pi/4) q[49];
cx q[48],q[49];
rz(pi/4) q[61];
swap q[61],q[48];
cx q[49],q[48];
rz(15*pi/4) q[48];
rz(3*pi/4) q[49];
cx q[61],q[48];
swap q[48],q[55];
swap q[49],q[48];
swap q[55],q[54];
swap q[10],q[55];
swap q[9],q[10];
cx q[10],q[11];
cx q[10],q[9];
rz(pi/4) q[9];
rz(15*pi/4) q[11];
cx q[10],q[11];
swap q[11],q[10];
cx q[10],q[9];
rz(15*pi/4) q[9];
swap q[9],q[10];
cx q[9],q[8];
rz(15*pi/4) q[8];
cx q[11],q[10];
cx q[20],q[9];
rz(15*pi/4) q[9];
swap q[20],q[9];
cx q[9],q[8];
rz(pi/4) q[8];
cx q[9],q[20];
rz(pi/2) q[20];
swap q[20],q[21];
cx q[21],q[8];
rz(15*pi/4) q[8];
cx q[9],q[8];
swap q[15],q[8];
sx q[21];
rz(pi/2) q[21];
cx q[48],q[55];
cx q[53],q[54];
rz(15*pi/4) q[54];
swap q[11],q[54];
rz(15*pi/4) q[55];
swap q[48],q[55];
cx q[54],q[55];
rz(15*pi/4) q[55];
swap q[48],q[55];
cx q[54],q[55];
rz(pi/4) q[55];
swap q[48],q[55];
cx q[54],q[55];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[55],q[10];
rz(15*pi/4) q[10];
swap q[9],q[10];
cx q[10],q[55];
cx q[10],q[9];
rz(pi/4) q[9];
rz(15*pi/4) q[55];
cx q[10],q[55];
rz(pi/2) q[55];
swap q[55],q[10];
cx q[10],q[9];
rz(15*pi/4) q[9];
sx q[10];
rz(pi/2) q[10];
swap q[9],q[10];
cx q[55],q[10];
swap q[54],q[55];
swap q[53],q[54];
cx q[55],q[48];
cx q[55],q[54];
rz(15*pi/4) q[54];
swap q[55],q[54];
cx q[54],q[11];
rz(pi/4) q[11];
cx q[54],q[55];
swap q[11],q[54];
rz(pi/2) q[55];
cx q[55],q[54];
rz(15*pi/4) q[54];
cx q[11],q[54];
swap q[53],q[54];
cx q[40],q[53];
rz(15*pi/4) q[53];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[54],q[55];
rz(15*pi/4) q[55];
swap q[48],q[55];
cx q[54],q[55];
rz(pi/4) q[55];
swap q[48],q[55];
cx q[54],q[55];
rz(pi/2) q[55];
cx q[55],q[48];
rz(15*pi/4) q[48];
sx q[55];
rz(pi/2) q[55];
swap q[48],q[55];
swap q[48],q[61];
cx q[54],q[55];
swap q[54],q[53];
cx q[53],q[40];
rz(15*pi/4) q[40];
cx q[53],q[54];
cx q[53],q[40];
swap q[40],q[53];
rz(pi/4) q[54];
cx q[53],q[54];
rz(-3*pi/4) q[53];
ry(pi/2) q[53];
rz(15*pi/4) q[54];
swap q[53],q[54];
cx q[40],q[53];
swap q[54],q[11];
swap q[11],q[10];
swap q[10],q[9];
swap q[9],q[20];
swap q[8],q[9];
swap q[15],q[8];
swap q[20],q[21];
cx q[21],q[22];
swap q[21],q[22];
swap q[22],q[23];
cx q[23],q[16];
swap q[16],q[17];
swap q[17],q[18];
swap q[23],q[16];
cx q[17],q[16];
sx q[17];
swap q[53],q[54];
swap q[54],q[11];
swap q[61],q[62];
swap q[62],q[19];
cx q[19],q[18];
swap q[17],q[18];
swap q[19],q[20];
cx q[20],q[9];
cx q[10],q[9];
cx q[21],q[20];
rz(pi/2) q[20];
swap q[19],q[20];
swap q[18],q[19];
cx q[20],q[9];
ry(-pi/2) q[9];
rz(-pi) q[9];
swap q[9],q[10];
cx q[10],q[11];
rz(15*pi/4) q[11];
swap q[12],q[11];
cx q[11],q[10];
rz(15*pi/4) q[10];
cx q[11],q[12];
cx q[11],q[10];
rz(pi/4) q[12];
swap q[12],q[11];
cx q[10],q[11];
cx q[10],q[55];
rz(15*pi/4) q[11];
cx q[12],q[11];
swap q[12],q[11];
swap q[19],q[20];
cx q[9],q[20];
cx q[19],q[20];
rz(pi/2) q[20];
sx q[20];
swap q[9],q[20];
swap q[19],q[20];
swap q[19],q[18];
cx q[17],q[18];
sx q[17];
rz(pi/2) q[18];
sx q[21];
cx q[20],q[21];
swap q[21],q[22];
swap q[22],q[23];
cx q[16],q[23];
cx q[16],q[17];
swap q[17],q[18];
cx q[19],q[18];
rz(pi/2) q[18];
sx q[18];
cx q[19],q[20];
sx q[19];
rz(pi/2) q[19];
swap q[20],q[19];
swap q[19],q[18];
cx q[17],q[18];
cx q[17],q[16];
ry(-pi/2) q[16];
rz(-pi) q[16];
sx q[17];
rz(pi/2) q[17];
swap q[16],q[17];
ry(-pi/2) q[18];
rz(-pi) q[18];
rz(pi/2) q[23];
sx q[23];
swap q[23],q[22];
rz(15*pi/4) q[55];
swap q[10],q[55];
swap q[10],q[9];
swap q[9],q[20];
swap q[8],q[9];
swap q[9],q[10];
swap q[15],q[8];
swap q[20],q[19];
swap q[19],q[18];
swap q[55],q[48];
swap q[48],q[61];
swap q[54],q[55];
swap q[55],q[48];
swap q[10],q[55];
swap q[61],q[62];
swap q[48],q[61];
swap q[62],q[63];
cx q[56],q[63];
rz(15*pi/4) q[63];
swap q[56],q[63];
cx q[63],q[18];
rz(pi/4) q[18];
cx q[63],q[56];
swap q[56],q[63];
cx q[63],q[18];
rz(15*pi/4) q[18];
swap q[63],q[62];
cx q[62],q[61];
rz(15*pi/4) q[61];
cx q[63],q[62];
rz(15*pi/4) q[62];
swap q[61],q[62];
cx q[63],q[62];
rz(pi/4) q[62];
swap q[63],q[62];
cx q[62],q[61];
swap q[63],q[62];
cx q[61],q[62];
swap q[61],q[48];
cx q[48],q[55];
rz(15*pi/4) q[55];
swap q[10],q[55];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[55],q[10];
rz(pi/4) q[10];
cx q[55],q[48];
swap q[10],q[55];
cx q[48],q[55];
cx q[48],q[61];
cx q[49],q[48];
rz(15*pi/4) q[48];
rz(15*pi/4) q[55];
cx q[10],q[55];
swap q[11],q[10];
rz(15*pi/4) q[61];
swap q[61],q[60];
cx q[49],q[60];
cx q[49],q[48];
rz(pi/4) q[60];
swap q[60],q[49];
cx q[48],q[49];
swap q[48],q[55];
swap q[48],q[61];
rz(15*pi/4) q[49];
cx q[60],q[49];
swap q[49],q[60];
rz(15*pi/4) q[62];
cx q[63],q[62];
swap q[56],q[63];
cx q[63],q[18];
swap q[18],q[19];
swap q[19],q[20];
cx q[9],q[20];
cx q[10],q[9];
rz(15*pi/4) q[9];
rz(15*pi/4) q[20];
swap q[20],q[9];
cx q[10],q[9];
rz(pi/4) q[9];
swap q[8],q[9];
swap q[8],q[21];
swap q[9],q[10];
cx q[9],q[20];
swap q[9],q[8];
cx q[20],q[21];
rz(15*pi/4) q[20];
swap q[20],q[19];
cx q[19],q[62];
rz(15*pi/4) q[21];
cx q[8],q[21];
swap q[22],q[21];
cx q[55],q[10];
rz(15*pi/4) q[10];
cx q[54],q[55];
swap q[54],q[11];
cx q[11],q[10];
rz(pi/4) q[10];
rz(15*pi/4) q[55];
swap q[55],q[54];
cx q[11],q[54];
swap q[10],q[11];
swap q[48],q[55];
cx q[54],q[11];
rz(15*pi/4) q[11];
cx q[10],q[11];
swap q[9],q[10];
swap q[10],q[11];
cx q[54],q[11];
rz(15*pi/4) q[11];
cx q[53],q[54];
rz(15*pi/4) q[54];
swap q[53],q[54];
cx q[54],q[11];
rz(pi/4) q[11];
cx q[54],q[53];
swap q[11],q[54];
cx q[53],q[54];
rz(15*pi/4) q[54];
cx q[11],q[54];
swap q[55],q[54];
swap q[10],q[55];
cx q[53],q[54];
cx q[40],q[53];
rz(15*pi/4) q[53];
rz(15*pi/4) q[54];
swap q[54],q[53];
cx q[40],q[53];
rz(pi/4) q[53];
swap q[40],q[53];
cx q[53],q[54];
swap q[40],q[53];
rz(pi/2) q[54];
cx q[54],q[53];
rz(15*pi/4) q[53];
cx q[40],q[53];
sx q[54];
rz(pi/2) q[54];
swap q[53],q[54];
rz(15*pi/4) q[62];
swap q[19],q[62];
cx q[63],q[62];
rz(15*pi/4) q[62];
swap q[63],q[62];
cx q[62],q[19];
rz(pi/4) q[19];
cx q[62],q[63];
swap q[63],q[62];
cx q[62],q[19];
rz(15*pi/4) q[19];
cx q[62],q[61];
rz(15*pi/4) q[61];
swap q[62],q[63];
cx q[56],q[63];
cx q[62],q[19];
swap q[19],q[20];
cx q[21],q[20];
cx q[8],q[21];
rz(15*pi/4) q[20];
rz(3*pi/4) q[21];
swap q[20],q[21];
cx q[8],q[21];
swap q[8],q[9];
cx q[9],q[20];
swap q[9],q[8];
rz(pi/2) q[20];
rz(pi/4) q[21];
cx q[20],q[21];
swap q[20],q[19];
rz(15*pi/4) q[21];
cx q[8],q[21];
swap q[8],q[9];
swap q[61],q[62];
rz(15*pi/4) q[63];
swap q[62],q[63];
cx q[56],q[63];
rz(pi/4) q[63];
swap q[62],q[63];
cx q[56],q[63];
cx q[63],q[62];
rz(15*pi/4) q[62];
swap q[62],q[63];
cx q[56],q[63];
swap q[62],q[61];
swap q[19],q[62];
cx q[61],q[60];
cx q[48],q[61];
rz(15*pi/4) q[60];
rz(15*pi/4) q[61];
swap q[48],q[61];
cx q[61],q[60];
rz(pi/4) q[60];
cx q[61],q[48];
swap q[60],q[61];
cx q[48],q[61];
cx q[48],q[55];
cx q[49],q[48];
rz(15*pi/4) q[48];
rz(15*pi/4) q[55];
swap q[55],q[48];
cx q[49],q[48];
rz(pi/4) q[48];
swap q[49],q[48];
cx q[48],q[55];
swap q[49],q[48];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[49],q[48];
cx q[55],q[10];
rz(15*pi/4) q[10];
swap q[55],q[10];
rz(15*pi/4) q[61];
cx q[60],q[61];
cx q[62],q[63];
cx q[19],q[62];
rz(15*pi/4) q[62];
rz(15*pi/4) q[63];
swap q[63],q[18];
cx q[19],q[18];
rz(pi/4) q[18];
cx q[19],q[62];
swap q[18],q[19];
swap q[56],q[63];
cx q[62],q[19];
rz(15*pi/4) q[19];
cx q[18],q[19];
cx q[20],q[19];
cx q[9],q[20];
rz(15*pi/4) q[19];
rz(15*pi/4) q[20];
swap q[19],q[20];
cx q[9],q[20];
rz(pi/4) q[20];
swap q[9],q[20];
cx q[20],q[19];
swap q[9],q[20];
cx q[19],q[20];
rz(5*pi/4) q[19];
rz(15*pi/4) q[20];
cx q[9],q[20];
swap q[8],q[9];
swap q[8],q[21];
cx q[9],q[10];
rz(15*pi/4) q[10];
swap q[9],q[10];
cx q[10],q[55];
cx q[10],q[9];
swap q[9],q[10];
swap q[15],q[8];
swap q[21],q[20];
swap q[8],q[21];
rz(pi/4) q[55];
cx q[10],q[55];
rz(15*pi/4) q[55];
swap q[10],q[55];
cx q[9],q[10];
cx q[55],q[54];
swap q[10],q[55];
cx q[11],q[10];
rz(15*pi/4) q[10];
rz(15*pi/4) q[54];
cx q[11],q[54];
cx q[11],q[10];
rz(pi/2) q[10];
rz(pi/4) q[54];
swap q[54],q[11];
cx q[10],q[11];
sx q[10];
rz(pi/2) q[10];
rz(15*pi/4) q[11];
cx q[54],q[11];
swap q[11],q[10];
cx q[62],q[61];
rz(15*pi/4) q[61];
cx q[63],q[62];
rz(15*pi/4) q[62];
swap q[61],q[62];
cx q[63],q[62];
rz(pi/4) q[62];
swap q[63],q[62];
cx q[62],q[61];
swap q[63],q[62];
cx q[61],q[62];
cx q[61],q[48];
rz(15*pi/4) q[48];
cx q[60],q[61];
rz(15*pi/4) q[61];
swap q[48],q[61];
swap q[48],q[49];
cx q[60],q[61];
cx q[60],q[49];
swap q[49],q[48];
rz(pi/4) q[61];
cx q[48],q[61];
cx q[48],q[55];
cx q[49],q[48];
rz(15*pi/4) q[48];
rz(15*pi/4) q[55];
swap q[55],q[48];
cx q[49],q[48];
rz(pi/4) q[48];
swap q[49],q[48];
cx q[48],q[55];
swap q[49],q[48];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[49],q[48];
cx q[55],q[10];
rz(15*pi/4) q[10];
swap q[55],q[10];
cx q[9],q[10];
rz(15*pi/4) q[10];
swap q[9],q[10];
cx q[10],q[55];
cx q[10],q[9];
rz(pi/2) q[9];
swap q[9],q[10];
rz(pi/4) q[55];
cx q[10],q[55];
sx q[10];
rz(pi/2) q[10];
swap q[9],q[10];
rz(15*pi/4) q[55];
cx q[10],q[55];
rz(15*pi/4) q[61];
cx q[60],q[61];
rz(15*pi/4) q[62];
cx q[63],q[62];
cx q[19],q[62];
cx q[18],q[19];
rz(15*pi/4) q[19];
rz(15*pi/4) q[62];
swap q[62],q[63];
cx q[18],q[63];
cx q[18],q[19];
swap q[19],q[62];
swap q[20],q[19];
rz(pi/4) q[63];
cx q[62],q[63];
cx q[62],q[61];
rz(15*pi/4) q[61];
rz(15*pi/4) q[63];
cx q[18],q[63];
swap q[19],q[18];
cx q[56],q[63];
swap q[62],q[19];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[20],q[19];
swap q[61],q[62];
cx q[19],q[62];
cx q[19],q[20];
swap q[20],q[19];
rz(pi/4) q[62];
cx q[19],q[62];
swap q[20],q[19];
rz(15*pi/4) q[62];
cx q[19],q[62];
swap q[20],q[19];
rz(15*pi/4) q[63];
swap q[18],q[63];
cx q[63],q[56];
rz(3*pi/4) q[56];
cx q[63],q[18];
rz(pi/4) q[18];
cx q[63],q[56];
swap q[18],q[63];
cx q[56],q[63];
rz(15*pi/4) q[63];
cx q[18],q[63];
swap q[17],q[18];
swap q[56],q[63];
cx q[63],q[62];
rz(15*pi/4) q[62];
swap q[63],q[62];
cx q[61],q[62];
rz(15*pi/4) q[62];
swap q[61],q[62];
cx q[62],q[63];
cx q[62],q[61];
swap q[61],q[62];
rz(pi/4) q[63];
cx q[62],q[63];
swap q[61],q[62];
swap q[48],q[61];
rz(15*pi/4) q[63];
cx q[62],q[63];
cx q[18],q[63];
cx q[17],q[18];
rz(15*pi/4) q[18];
swap q[19],q[62];
swap q[20],q[19];
cx q[62],q[61];
rz(15*pi/4) q[61];
swap q[62],q[61];
cx q[60],q[61];
rz(15*pi/4) q[61];
swap q[60],q[61];
cx q[61],q[62];
cx q[61],q[60];
swap q[60],q[61];
rz(pi/4) q[62];
cx q[61],q[62];
swap q[61],q[48];
cx q[48],q[55];
cx q[49],q[48];
rz(15*pi/4) q[48];
rz(15*pi/4) q[55];
swap q[55],q[48];
cx q[49],q[48];
rz(pi/4) q[48];
swap q[49],q[48];
cx q[48],q[55];
swap q[49],q[48];
rz(pi/2) q[55];
cx q[55],q[48];
rz(15*pi/4) q[48];
cx q[49],q[48];
sx q[55];
rz(pi/2) q[55];
swap q[60],q[61];
rz(15*pi/4) q[62];
cx q[61],q[62];
swap q[60],q[61];
cx q[61],q[62];
rz(15*pi/4) q[62];
swap q[19],q[62];
cx q[62],q[61];
rz(15*pi/4) q[61];
cx q[62],q[19];
rz(pi/4) q[19];
cx q[62],q[61];
swap q[19],q[62];
cx q[61],q[62];
cx q[61],q[48];
rz(15*pi/4) q[48];
cx q[60],q[61];
rz(15*pi/4) q[61];
swap q[48],q[61];
swap q[48],q[49];
cx q[60],q[61];
cx q[60],q[49];
rz(pi/2) q[49];
swap q[49],q[48];
rz(pi/4) q[61];
cx q[48],q[61];
sx q[48];
rz(pi/2) q[48];
rz(15*pi/4) q[61];
cx q[60],q[61];
rz(15*pi/4) q[62];
cx q[19],q[62];
rz(15*pi/4) q[63];
swap q[63],q[18];
cx q[17],q[18];
rz(pi/4) q[18];
swap q[63],q[18];
cx q[17],q[18];
cx q[18],q[63];
rz(3*pi/4) q[18];
rz(15*pi/4) q[63];
swap q[63],q[18];
cx q[17],q[18];
cx q[63],q[62];
rz(15*pi/4) q[62];
swap q[63],q[62];
swap q[62],q[19];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[61],q[62];
swap q[63],q[18];
swap q[18],q[19];
cx q[20],q[19];
rz(pi/4) q[19];
swap q[18],q[19];
cx q[20],q[19];
cx q[19],q[18];
rz(15*pi/4) q[18];
cx q[19],q[62];
rz(15*pi/4) q[62];
swap q[19],q[62];
cx q[61],q[62];
rz(15*pi/4) q[62];
swap q[61],q[62];
cx q[62],q[19];
rz(pi/4) q[19];
cx q[62],q[61];
rz(pi/2) q[61];
swap q[61],q[62];
cx q[62],q[19];
rz(15*pi/4) q[19];
sx q[62];
rz(pi/2) q[62];
swap q[61],q[62];
cx q[62],q[19];
swap q[18],q[19];
swap q[17],q[18];
cx q[20],q[19];
swap q[21],q[20];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[20],q[19];
cx q[18],q[19];
rz(15*pi/4) q[19];
swap q[20],q[19];
cx q[18],q[19];
rz(pi/4) q[19];
swap q[20],q[19];
cx q[18],q[19];
rz(pi/2) q[19];
cx q[19],q[20];
swap q[18],q[19];
cx q[18],q[17];
rz(15*pi/4) q[17];
rz(15*pi/4) q[20];
cx q[19],q[20];
swap q[18],q[19];
swap q[17],q[18];
swap q[16],q[17];
swap q[21],q[20];
cx q[20],q[19];
rz(15*pi/4) q[19];
swap q[20],q[19];
cx q[19],q[18];
rz(pi/4) q[18];
cx q[19],q[20];
rz(pi/2) q[20];
swap q[20],q[19];
cx q[19],q[18];
rz(15*pi/4) q[18];
sx q[19];
rz(pi/2) q[19];
swap q[20],q[19];
cx q[19],q[18];
cx q[17],q[18];
cx q[16],q[17];
rz(15*pi/4) q[17];
rz(15*pi/4) q[18];
swap q[18],q[17];
cx q[16],q[17];
rz(pi/4) q[17];
swap q[18],q[17];
cx q[16],q[17];
cx q[17],q[18];
rz(-3*pi/4) q[17];
ry(pi/2) q[17];
rz(15*pi/4) q[18];
swap q[18],q[17];
cx q[16],q[17];
