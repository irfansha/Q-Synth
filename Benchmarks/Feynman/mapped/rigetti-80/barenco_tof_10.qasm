OPENQASM 2.0;
include "qelib1.inc";
qreg q[80];
rz(pi/2) q[9];
rz(pi/2) q[19];
rz(pi/2) q[40];
ry(-pi/2) q[42];
rz(-pi) q[42];
cx q[42],q[43];
rz(3*pi/4) q[44];
swap q[44],q[43];
cx q[43],q[42];
rz(15*pi/4) q[42];
cx q[43],q[44];
cx q[43],q[42];
swap q[42],q[43];
rz(pi/4) q[44];
cx q[43],q[44];
rz(15*pi/4) q[44];
swap q[44],q[43];
cx q[42],q[43];
sx q[42];
rz(pi/2) q[42];
cx q[42],q[41];
swap q[40],q[41];
cx q[41],q[42];
cx q[41],q[40];
rz(pi/4) q[40];
rz(15*pi/4) q[42];
cx q[41],q[42];
cx q[41],q[40];
sx q[41];
rz(pi/2) q[41];
cx q[44],q[43];
swap q[44],q[43];
swap q[47],q[40];
cx q[41],q[40];
rz(pi/2) q[48];
rz(pi/2) q[52];
cx q[52],q[41];
rz(15*pi/4) q[41];
swap q[40],q[41];
cx q[52],q[41];
rz(pi/4) q[41];
swap q[40],q[41];
cx q[52],q[41];
swap q[40],q[41];
cx q[52],q[41];
swap q[40],q[41];
sx q[52];
rz(pi/2) q[52];
swap q[52],q[51];
swap q[51],q[50];
cx q[50],q[49];
swap q[48],q[49];
cx q[49],q[50];
cx q[49],q[48];
rz(pi/4) q[48];
rz(15*pi/4) q[50];
cx q[49],q[50];
cx q[49],q[48];
sx q[49];
rz(pi/2) q[49];
rz(pi/2) q[59];
cx q[49],q[60];
swap q[59],q[60];
cx q[60],q[49];
rz(15*pi/4) q[49];
cx q[60],q[59];
rz(pi/4) q[59];
cx q[60],q[49];
cx q[60],q[59];
sx q[60];
rz(pi/2) q[60];
cx q[60],q[61];
swap q[60],q[61];
rz(pi/2) q[62];
cx q[62],q[61];
rz(15*pi/4) q[61];
swap q[60],q[61];
cx q[62],q[61];
rz(pi/4) q[61];
swap q[60],q[61];
cx q[62],q[61];
swap q[60],q[61];
cx q[62],q[61];
sx q[62];
rz(pi/2) q[62];
cx q[62],q[63];
cx q[19],q[62];
rz(15*pi/4) q[62];
swap q[63],q[18];
cx q[19],q[18];
rz(pi/4) q[18];
cx q[19],q[62];
cx q[19],q[18];
sx q[19];
rz(pi/2) q[19];
cx q[19],q[20];
swap q[9],q[20];
cx q[20],q[19];
rz(15*pi/4) q[19];
cx q[20],q[9];
rz(pi/4) q[9];
cx q[20],q[19];
cx q[20],q[9];
sx q[20];
rz(pi/2) q[20];
cx q[20],q[21];
rz(15*pi/4) q[21];
swap q[22],q[21];
cx q[21],q[20];
rz(15*pi/4) q[20];
cx q[21],q[22];
cx q[21],q[20];
rz(pi/4) q[22];
swap q[22],q[21];
cx q[20],q[21];
rz(-pi/4) q[20];
rx(-pi/2) q[20];
cx q[20],q[19];
rz(pi/4) q[19];
x q[19];
cx q[20],q[9];
rz(15*pi/4) q[9];
sx q[9];
cx q[20],q[19];
swap q[9],q[20];
rz(pi/2) q[19];
cx q[19],q[20];
sx q[19];
cx q[19],q[62];
cx q[19],q[18];
rz(15*pi/4) q[18];
sx q[18];
cx q[22],q[21];
rz(pi/4) q[62];
x q[62];
cx q[19],q[62];
swap q[18],q[19];
rz(pi/2) q[62];
cx q[62],q[19];
sx q[62];
swap q[62],q[61];
cx q[61],q[60];
rz(pi/4) q[60];
x q[60];
cx q[61],q[62];
cx q[61],q[60];
rz(pi/2) q[60];
rz(15*pi/4) q[62];
sx q[62];
swap q[62],q[61];
cx q[60],q[61];
sx q[60];
cx q[60],q[49];
rz(pi/4) q[49];
x q[49];
cx q[60],q[59];
rz(15*pi/4) q[59];
sx q[59];
cx q[60],q[49];
rz(pi/2) q[49];
swap q[59],q[60];
cx q[49],q[60];
sx q[49];
cx q[49],q[50];
cx q[49],q[48];
rz(15*pi/4) q[48];
sx q[48];
rz(pi/4) q[50];
x q[50];
cx q[49],q[50];
swap q[48],q[49];
rz(pi/2) q[50];
cx q[50],q[49];
sx q[50];
swap q[50],q[51];
swap q[51],q[52];
cx q[52],q[41];
rz(pi/4) q[41];
x q[41];
swap q[40],q[41];
cx q[52],q[41];
rz(15*pi/4) q[41];
sx q[41];
swap q[40],q[41];
cx q[52],q[41];
rz(pi/2) q[41];
cx q[41],q[40];
sx q[41];
cx q[41],q[42];
rz(pi/4) q[42];
swap q[47],q[40];
cx q[41],q[40];
rz(-pi/4) q[40];
rx(-pi/2) q[40];
cx q[41],q[42];
swap q[40],q[41];
cx q[42],q[41];
ry(-pi/2) q[42];
rz(-3*pi/4) q[42];
cx q[42],q[43];
rz(pi/4) q[43];
swap q[44],q[43];
cx q[42],q[43];
rz(15*pi/4) q[43];
swap q[44],q[43];
cx q[42],q[43];
rz(pi/2) q[43];
cx q[43],q[44];
sx q[43];
rz(pi/2) q[43];
rz(pi/4) q[44];
swap q[44],q[43];
cx q[42],q[43];
sx q[42];
rz(pi/2) q[42];
cx q[42],q[41];
sx q[41];
rz(pi/4) q[41];
swap q[40],q[41];
cx q[41],q[42];
rz(15*pi/4) q[42];
cx q[41],q[42];
cx q[41],q[40];
sx q[41];
rz(pi/2) q[41];
swap q[47],q[40];
cx q[41],q[40];
sx q[40];
rz(pi/4) q[40];
cx q[52],q[41];
rz(15*pi/4) q[41];
cx q[52],q[41];
swap q[40],q[41];
cx q[52],q[41];
sx q[52];
rz(pi/2) q[52];
swap q[52],q[51];
swap q[51],q[50];
cx q[50],q[49];
sx q[49];
rz(pi/4) q[49];
swap q[48],q[49];
cx q[49],q[50];
rz(15*pi/4) q[50];
cx q[49],q[50];
cx q[49],q[48];
sx q[49];
rz(pi/2) q[49];
cx q[49],q[60];
sx q[60];
rz(pi/4) q[60];
swap q[59],q[60];
cx q[60],q[49];
rz(15*pi/4) q[49];
cx q[60],q[49];
cx q[60],q[59];
sx q[60];
rz(pi/2) q[60];
cx q[60],q[61];
sx q[61];
rz(pi/4) q[61];
swap q[60],q[61];
cx q[62],q[61];
rz(15*pi/4) q[61];
cx q[62],q[61];
swap q[60],q[61];
cx q[62],q[61];
sx q[62];
rz(pi/2) q[62];
cx q[62],q[19];
sx q[19];
rz(pi/4) q[19];
swap q[18],q[19];
cx q[19],q[62];
rz(15*pi/4) q[62];
cx q[19],q[62];
cx q[19],q[18];
sx q[19];
rz(pi/2) q[19];
cx q[19],q[20];
sx q[20];
rz(pi/4) q[20];
swap q[9],q[20];
cx q[20],q[19];
rz(15*pi/4) q[19];
cx q[20],q[19];
cx q[20],q[9];
sx q[20];
rz(pi/2) q[20];
cx q[20],q[21];
rz(pi/4) q[21];
swap q[22],q[21];
cx q[21],q[20];
rz(pi/4) q[20];
cx q[21],q[22];
cx q[21],q[20];
rz(15*pi/4) q[22];
swap q[22],q[21];
cx q[20],q[21];
rz(3*pi/4) q[20];
ry(pi/2) q[20];
cx q[20],q[19];
rz(pi/4) q[19];
cx q[20],q[9];
rz(15*pi/4) q[9];
cx q[20],q[19];
swap q[9],q[20];
rz(pi/2) q[19];
cx q[19],q[20];
cx q[9],q[20];
sx q[19];
rz(pi/2) q[19];
cx q[19],q[62];
cx q[19],q[18];
rz(15*pi/4) q[18];
cx q[22],q[21];
rz(pi/4) q[62];
cx q[19],q[62];
swap q[18],q[19];
rz(pi/2) q[62];
cx q[62],q[19];
cx q[18],q[19];
sx q[62];
rz(pi/2) q[62];
swap q[62],q[61];
cx q[61],q[60];
rz(pi/4) q[60];
cx q[61],q[62];
cx q[61],q[60];
rz(pi/2) q[60];
rz(15*pi/4) q[62];
swap q[62],q[61];
cx q[60],q[61];
sx q[60];
rz(pi/2) q[60];
cx q[60],q[49];
rz(pi/4) q[49];
cx q[60],q[59];
rz(15*pi/4) q[59];
cx q[60],q[49];
rz(pi/2) q[49];
swap q[59],q[60];
cx q[49],q[60];
sx q[49];
rz(pi/2) q[49];
cx q[49],q[50];
cx q[49],q[48];
rz(15*pi/4) q[48];
rz(pi/4) q[50];
cx q[49],q[50];
swap q[48],q[49];
rz(pi/2) q[50];
cx q[50],q[49];
cx q[48],q[49];
sx q[50];
rz(pi/2) q[50];
swap q[50],q[51];
swap q[51],q[52];
swap q[52],q[41];
cx q[41],q[40];
rz(pi/4) q[40];
cx q[41],q[52];
cx q[41],q[40];
rz(pi/2) q[40];
rz(15*pi/4) q[52];
swap q[52],q[41];
cx q[40],q[41];
sx q[40];
rz(pi/2) q[40];
cx q[52],q[41];
swap q[42],q[41];
cx q[40],q[41];
cx q[40],q[47];
rz(pi/4) q[41];
cx q[40],q[41];
rz(pi/2) q[41];
rz(15*pi/4) q[47];
swap q[47],q[40];
cx q[41],q[40];
sx q[41];
rz(pi/2) q[41];
cx q[47],q[40];
cx q[59],q[60];
cx q[62],q[61];
