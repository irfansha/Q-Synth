// Initializing random generator with seed:  0
OPENQASM 2.0;
include "qelib1.inc";
qreg q[16];
cx q[13],q[0];
cx q[4],q[8];
x q[0];
x q[8];
cx q[13],q[4];
cx q[0],q[13];
ry(-0.25) q[13];
cx q[8],q[13];
ry(0.25) q[13];
cx q[4],q[13];
ry(-0.25) q[13];
cx q[8],q[13];
ry(0.25) q[13];
cx q[0],q[13];
ry(-0.25) q[13];
cx q[8],q[13];
ry(0.25) q[13];
cx q[4],q[13];
ry(-0.25) q[13];
cx q[8],q[13];
ry(0.25) q[13];
cx q[13],q[4];
x q[0];
x q[8];
cx q[13],q[0];
cx q[4],q[8];
cx q[12],q[14];
cx q[15],q[4];
x q[14];
x q[4];
cx q[12],q[15];
cx q[14],q[12];
ry(-0.25) q[12];
cx q[4],q[12];
ry(0.25) q[12];
cx q[15],q[12];
ry(-0.25) q[12];
cx q[4],q[12];
ry(0.25) q[12];
cx q[14],q[12];
ry(-0.25) q[12];
cx q[4],q[12];
ry(0.25) q[12];
cx q[15],q[12];
ry(-0.25) q[12];
cx q[4],q[12];
ry(0.25) q[12];
cx q[12],q[15];
x q[14];
x q[4];
cx q[12],q[14];
cx q[15],q[4];
cx q[11],q[9];
cx q[3],q[8];
x q[9];
x q[8];
cx q[11],q[3];
cx q[9],q[11];
ry(-0.25) q[11];
cx q[8],q[11];
ry(0.25) q[11];
cx q[3],q[11];
ry(-0.25) q[11];
cx q[8],q[11];
ry(0.25) q[11];
cx q[9],q[11];
ry(-0.25) q[11];
cx q[8],q[11];
ry(0.25) q[11];
cx q[3],q[11];
ry(-0.25) q[11];
cx q[8],q[11];
ry(0.25) q[11];
cx q[11],q[3];
x q[9];
x q[8];
cx q[11],q[9];
cx q[3],q[8];
s q[2];
sx q[2];
sx q[9];
cx q[2],q[9];
rx(1.0) q[2];
rz(1.0) q[9];
cx q[2],q[9];
sxdg q[9];
sxdg q[2];
sdg q[2];
s q[14];
sx q[14];
sx q[8];
cx q[14],q[8];
rx(1.0) q[14];
rz(1.0) q[8];
cx q[14],q[8];
sxdg q[8];
sxdg q[14];
sdg q[14];
s q[1];
sx q[1];
sx q[9];
cx q[1],q[9];
rx(1.0) q[1];
rz(1.0) q[9];
cx q[1],q[9];
sxdg q[9];
sxdg q[1];
sdg q[1];
s q[7];
sx q[7];
sx q[10];
cx q[7],q[10];
rx(1.0) q[7];
rz(1.0) q[10];
cx q[7],q[10];
sxdg q[10];
sxdg q[7];
sdg q[7];
s q[6];
sx q[6];
sx q[11];
cx q[6],q[11];
rx(1.0) q[6];
rz(1.0) q[11];
cx q[6],q[11];
sxdg q[11];
sxdg q[6];
sdg q[6];
cx q[6],q[8];
cx q[7],q[13];
x q[8];
x q[13];
cx q[6],q[7];
cx q[8],q[6];
ry(-0.25) q[6];
cx q[13],q[6];
ry(0.25) q[6];
cx q[7],q[6];
ry(-0.25) q[6];
cx q[13],q[6];
ry(0.25) q[6];
cx q[8],q[6];
ry(-0.25) q[6];
cx q[13],q[6];
ry(0.25) q[6];
cx q[7],q[6];
ry(-0.25) q[6];
cx q[13],q[6];
ry(0.25) q[6];
cx q[6],q[7];
x q[8];
x q[13];
cx q[6],q[8];
cx q[7],q[13];
cx q[1],q[12];
cx q[8],q[0];
x q[12];
x q[0];
cx q[1],q[8];
cx q[12],q[1];
ry(-0.25) q[1];
cx q[0],q[1];
ry(0.25) q[1];
cx q[8],q[1];
ry(-0.25) q[1];
cx q[0],q[1];
ry(0.25) q[1];
cx q[12],q[1];
ry(-0.25) q[1];
cx q[0],q[1];
ry(0.25) q[1];
cx q[8],q[1];
ry(-0.25) q[1];
cx q[0],q[1];
ry(0.25) q[1];
cx q[1],q[8];
x q[12];
x q[0];
cx q[1],q[12];
cx q[8],q[0];
s q[11];
sx q[11];
sx q[12];
cx q[11],q[12];
rx(1.0) q[11];
rz(1.0) q[12];
cx q[11],q[12];
sxdg q[12];
sxdg q[11];
sdg q[11];
s q[13];
sx q[13];
sx q[15];
cx q[13],q[15];
rx(1.0) q[13];
rz(1.0) q[15];
cx q[13],q[15];
sxdg q[15];
sxdg q[13];
sdg q[13];
cx q[7],q[11];
cx q[5],q[14];
x q[11];
x q[14];
cx q[7],q[5];
cx q[11],q[7];
ry(-0.25) q[7];
cx q[14],q[7];
ry(0.25) q[7];
cx q[5],q[7];
ry(-0.25) q[7];
cx q[14],q[7];
ry(0.25) q[7];
cx q[11],q[7];
ry(-0.25) q[7];
cx q[14],q[7];
ry(0.25) q[7];
cx q[5],q[7];
ry(-0.25) q[7];
cx q[14],q[7];
ry(0.25) q[7];
cx q[7],q[5];
x q[11];
x q[14];
cx q[7],q[11];
cx q[5],q[14];
s q[14];
sx q[14];
sx q[6];
cx q[14],q[6];
rx(1.0) q[14];
rz(1.0) q[6];
cx q[14],q[6];
sxdg q[6];
sxdg q[14];
sdg q[14];
s q[12];
sx q[12];
sx q[7];
cx q[12],q[7];
rx(1.0) q[12];
rz(1.0) q[7];
cx q[12],q[7];
sxdg q[7];
sxdg q[12];
sdg q[12];
s q[1];
sx q[1];
sx q[14];
cx q[1],q[14];
rx(1.0) q[1];
rz(1.0) q[14];
cx q[1],q[14];
sxdg q[14];
sxdg q[1];
sdg q[1];
s q[14];
sx q[14];
sx q[10];
cx q[14],q[10];
rx(1.0) q[14];
rz(1.0) q[10];
cx q[14],q[10];
sxdg q[10];
sxdg q[14];
sdg q[14];
cx q[3],q[4];
cx q[8],q[14];
x q[4];
x q[14];
cx q[3],q[8];
cx q[4],q[3];
ry(-0.25) q[3];
cx q[14],q[3];
ry(0.25) q[3];
cx q[8],q[3];
ry(-0.25) q[3];
cx q[14],q[3];
ry(0.25) q[3];
cx q[4],q[3];
ry(-0.25) q[3];
cx q[14],q[3];
ry(0.25) q[3];
cx q[8],q[3];
ry(-0.25) q[3];
cx q[14],q[3];
ry(0.25) q[3];
cx q[3],q[8];
x q[4];
x q[14];
cx q[3],q[4];
cx q[8],q[14];
s q[13];
sx q[13];
sx q[10];
cx q[13],q[10];
rx(1.0) q[13];
rz(1.0) q[10];
cx q[13],q[10];
sxdg q[10];
sxdg q[13];
sdg q[13];
s q[7];
sx q[7];
sx q[9];
cx q[7],q[9];
rx(1.0) q[7];
rz(1.0) q[9];
cx q[7],q[9];
sxdg q[9];
sxdg q[7];
sdg q[7];
s q[5];
sx q[5];
sx q[12];
cx q[5],q[12];
rx(1.0) q[5];
rz(1.0) q[12];
cx q[5],q[12];
sxdg q[12];
sxdg q[5];
sdg q[5];
s q[2];
sx q[2];
sx q[9];
cx q[2],q[9];
rx(1.0) q[2];
rz(1.0) q[9];
cx q[2],q[9];
sxdg q[9];
sxdg q[2];
sdg q[2];
s q[0];
sx q[0];
sx q[5];
cx q[0],q[5];
rx(1.0) q[0];
rz(1.0) q[5];
cx q[0],q[5];
sxdg q[5];
sxdg q[0];
sdg q[0];
cx q[15],q[1];
cx q[14],q[10];
x q[1];
x q[10];
cx q[15],q[14];
cx q[1],q[15];
ry(-0.25) q[15];
cx q[10],q[15];
ry(0.25) q[15];
cx q[14],q[15];
ry(-0.25) q[15];
cx q[10],q[15];
ry(0.25) q[15];
cx q[1],q[15];
ry(-0.25) q[15];
cx q[10],q[15];
ry(0.25) q[15];
cx q[14],q[15];
ry(-0.25) q[15];
cx q[10],q[15];
ry(0.25) q[15];
cx q[15],q[14];
x q[1];
x q[10];
cx q[15],q[1];
cx q[14],q[10];
s q[14];
sx q[14];
sx q[4];
cx q[14],q[4];
rx(1.0) q[14];
rz(1.0) q[4];
cx q[14],q[4];
sxdg q[4];
sxdg q[14];
sdg q[14];
s q[14];
sx q[14];
sx q[2];
cx q[14],q[2];
rx(1.0) q[14];
rz(1.0) q[2];
cx q[14],q[2];
sxdg q[2];
sxdg q[14];
sdg q[14];
cx q[8],q[15];
cx q[12],q[3];
x q[15];
x q[3];
cx q[8],q[12];
cx q[15],q[8];
ry(-0.25) q[8];
cx q[3],q[8];
ry(0.25) q[8];
cx q[12],q[8];
ry(-0.25) q[8];
cx q[3],q[8];
ry(0.25) q[8];
cx q[15],q[8];
ry(-0.25) q[8];
cx q[3],q[8];
ry(0.25) q[8];
cx q[12],q[8];
ry(-0.25) q[8];
cx q[3],q[8];
ry(0.25) q[8];
cx q[8],q[12];
x q[15];
x q[3];
cx q[8],q[15];
cx q[12],q[3];
s q[9];
sx q[9];
sx q[13];
cx q[9],q[13];
rx(1.0) q[9];
rz(1.0) q[13];
cx q[9],q[13];
sxdg q[13];
sxdg q[9];
sdg q[9];
cx q[14],q[7];
cx q[10],q[13];
x q[7];
x q[13];
cx q[14],q[10];
cx q[7],q[14];
ry(-0.25) q[14];
cx q[13],q[14];
ry(0.25) q[14];
cx q[10],q[14];
ry(-0.25) q[14];
cx q[13],q[14];
ry(0.25) q[14];
cx q[7],q[14];
ry(-0.25) q[14];
cx q[13],q[14];
ry(0.25) q[14];
cx q[10],q[14];
ry(-0.25) q[14];
cx q[13],q[14];
ry(0.25) q[14];
cx q[14],q[10];
x q[7];
x q[13];
cx q[14],q[7];
cx q[10],q[13];
cx q[2],q[5];
cx q[9],q[1];
x q[5];
x q[1];
cx q[2],q[9];
cx q[5],q[2];
ry(-0.25) q[2];
cx q[1],q[2];
ry(0.25) q[2];
cx q[9],q[2];
ry(-0.25) q[2];
cx q[1],q[2];
ry(0.25) q[2];
cx q[5],q[2];
ry(-0.25) q[2];
cx q[1],q[2];
ry(0.25) q[2];
cx q[9],q[2];
ry(-0.25) q[2];
cx q[1],q[2];
ry(0.25) q[2];
cx q[2],q[9];
x q[5];
x q[1];
cx q[2],q[5];
cx q[9],q[1];
cx q[10],q[13];
cx q[3],q[14];
x q[13];
x q[14];
cx q[10],q[3];
cx q[13],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[3],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[13],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[3],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[10],q[3];
x q[13];
x q[14];
cx q[10],q[13];
cx q[3],q[14];
s q[1];
sx q[1];
sx q[8];
cx q[1],q[8];
rx(1.0) q[1];
rz(1.0) q[8];
cx q[1],q[8];
sxdg q[8];
sxdg q[1];
sdg q[1];
s q[12];
sx q[12];
sx q[11];
cx q[12],q[11];
rx(1.0) q[12];
rz(1.0) q[11];
cx q[12],q[11];
sxdg q[11];
sxdg q[12];
sdg q[12];
s q[6];
sx q[6];
sx q[10];
cx q[6],q[10];
rx(1.0) q[6];
rz(1.0) q[10];
cx q[6],q[10];
sxdg q[10];
sxdg q[6];
sdg q[6];
s q[12];
sx q[12];
sx q[3];
cx q[12],q[3];
rx(1.0) q[12];
rz(1.0) q[3];
cx q[12],q[3];
sxdg q[3];
sxdg q[12];
sdg q[12];
s q[0];
sx q[0];
sx q[7];
cx q[0],q[7];
rx(1.0) q[0];
rz(1.0) q[7];
cx q[0],q[7];
sxdg q[7];
sxdg q[0];
sdg q[0];
s q[1];
sx q[1];
sx q[0];
cx q[1],q[0];
rx(1.0) q[1];
rz(1.0) q[0];
cx q[1],q[0];
sxdg q[0];
sxdg q[1];
sdg q[1];
s q[6];
sx q[6];
sx q[3];
cx q[6],q[3];
rx(1.0) q[6];
rz(1.0) q[3];
cx q[6],q[3];
sxdg q[3];
sxdg q[6];
sdg q[6];
s q[13];
sx q[13];
sx q[11];
cx q[13],q[11];
rx(1.0) q[13];
rz(1.0) q[11];
cx q[13],q[11];
sxdg q[11];
sxdg q[13];
sdg q[13];
s q[9];
sx q[9];
sx q[1];
cx q[9],q[1];
rx(1.0) q[9];
rz(1.0) q[1];
cx q[9],q[1];
sxdg q[1];
sxdg q[9];
sdg q[9];
s q[2];
sx q[2];
sx q[6];
cx q[2],q[6];
rx(1.0) q[2];
rz(1.0) q[6];
cx q[2],q[6];
sxdg q[6];
sxdg q[2];
sdg q[2];
s q[3];
sx q[3];
sx q[15];
cx q[3],q[15];
rx(1.0) q[3];
rz(1.0) q[15];
cx q[3],q[15];
sxdg q[15];
sxdg q[3];
sdg q[3];
s q[8];
sx q[8];
sx q[0];
cx q[8],q[0];
rx(1.0) q[8];
rz(1.0) q[0];
cx q[8],q[0];
sxdg q[0];
sxdg q[8];
sdg q[8];
cx q[3],q[13];
cx q[4],q[1];
x q[13];
x q[1];
cx q[3],q[4];
cx q[13],q[3];
ry(-0.25) q[3];
cx q[1],q[3];
ry(0.25) q[3];
cx q[4],q[3];
ry(-0.25) q[3];
cx q[1],q[3];
ry(0.25) q[3];
cx q[13],q[3];
ry(-0.25) q[3];
cx q[1],q[3];
ry(0.25) q[3];
cx q[4],q[3];
ry(-0.25) q[3];
cx q[1],q[3];
ry(0.25) q[3];
cx q[3],q[4];
x q[13];
x q[1];
cx q[3],q[13];
cx q[4],q[1];
s q[10];
sx q[10];
sx q[2];
cx q[10],q[2];
rx(1.0) q[10];
rz(1.0) q[2];
cx q[10],q[2];
sxdg q[2];
sxdg q[10];
sdg q[10];
cx q[11],q[6];
cx q[2],q[0];
x q[6];
x q[0];
cx q[11],q[2];
cx q[6],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[2],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[6],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[2],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[11],q[2];
x q[6];
x q[0];
cx q[11],q[6];
cx q[2],q[0];
cx q[1],q[9];
cx q[15],q[11];
x q[9];
x q[11];
cx q[1],q[15];
cx q[9],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[15],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[9],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[15],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[1],q[15];
x q[9];
x q[11];
cx q[1],q[9];
cx q[15],q[11];
cx q[6],q[4];
cx q[5],q[11];
x q[4];
x q[11];
cx q[6],q[5];
cx q[4],q[6];
ry(-0.25) q[6];
cx q[11],q[6];
ry(0.25) q[6];
cx q[5],q[6];
ry(-0.25) q[6];
cx q[11],q[6];
ry(0.25) q[6];
cx q[4],q[6];
ry(-0.25) q[6];
cx q[11],q[6];
ry(0.25) q[6];
cx q[5],q[6];
ry(-0.25) q[6];
cx q[11],q[6];
ry(0.25) q[6];
cx q[6],q[5];
x q[4];
x q[11];
cx q[6],q[4];
cx q[5],q[11];
cx q[5],q[11];
cx q[10],q[3];
x q[11];
x q[3];
cx q[5],q[10];
cx q[11],q[5];
ry(-0.25) q[5];
cx q[3],q[5];
ry(0.25) q[5];
cx q[10],q[5];
ry(-0.25) q[5];
cx q[3],q[5];
ry(0.25) q[5];
cx q[11],q[5];
ry(-0.25) q[5];
cx q[3],q[5];
ry(0.25) q[5];
cx q[10],q[5];
ry(-0.25) q[5];
cx q[3],q[5];
ry(0.25) q[5];
cx q[5],q[10];
x q[11];
x q[3];
cx q[5],q[11];
cx q[10],q[3];
s q[13];
sx q[13];
sx q[5];
cx q[13],q[5];
rx(1.0) q[13];
rz(1.0) q[5];
cx q[13],q[5];
sxdg q[5];
sxdg q[13];
sdg q[13];
s q[8];
sx q[8];
sx q[10];
cx q[8],q[10];
rx(1.0) q[8];
rz(1.0) q[10];
cx q[8],q[10];
sxdg q[10];
sxdg q[8];
sdg q[8];
cx q[3],q[9];
cx q[7],q[10];
x q[9];
x q[10];
cx q[3],q[7];
cx q[9],q[3];
ry(-0.25) q[3];
cx q[10],q[3];
ry(0.25) q[3];
cx q[7],q[3];
ry(-0.25) q[3];
cx q[10],q[3];
ry(0.25) q[3];
cx q[9],q[3];
ry(-0.25) q[3];
cx q[10],q[3];
ry(0.25) q[3];
cx q[7],q[3];
ry(-0.25) q[3];
cx q[10],q[3];
ry(0.25) q[3];
cx q[3],q[7];
x q[9];
x q[10];
cx q[3],q[9];
cx q[7],q[10];
s q[7];
sx q[7];
sx q[0];
cx q[7],q[0];
rx(1.0) q[7];
rz(1.0) q[0];
cx q[7],q[0];
sxdg q[0];
sxdg q[7];
sdg q[7];
cx q[9],q[10];
cx q[5],q[6];
x q[10];
x q[6];
cx q[9],q[5];
cx q[10],q[9];
ry(-0.25) q[9];
cx q[6],q[9];
ry(0.25) q[9];
cx q[5],q[9];
ry(-0.25) q[9];
cx q[6],q[9];
ry(0.25) q[9];
cx q[10],q[9];
ry(-0.25) q[9];
cx q[6],q[9];
ry(0.25) q[9];
cx q[5],q[9];
ry(-0.25) q[9];
cx q[6],q[9];
ry(0.25) q[9];
cx q[9],q[5];
x q[10];
x q[6];
cx q[9],q[10];
cx q[5],q[6];
cx q[4],q[8];
cx q[11],q[0];
x q[8];
x q[0];
cx q[4],q[11];
cx q[8],q[4];
ry(-0.25) q[4];
cx q[0],q[4];
ry(0.25) q[4];
cx q[11],q[4];
ry(-0.25) q[4];
cx q[0],q[4];
ry(0.25) q[4];
cx q[8],q[4];
ry(-0.25) q[4];
cx q[0],q[4];
ry(0.25) q[4];
cx q[11],q[4];
ry(-0.25) q[4];
cx q[0],q[4];
ry(0.25) q[4];
cx q[4],q[11];
x q[8];
x q[0];
cx q[4],q[8];
cx q[11],q[0];
cx q[2],q[5];
cx q[11],q[0];
x q[5];
x q[0];
cx q[2],q[11];
cx q[5],q[2];
ry(-0.25) q[2];
cx q[0],q[2];
ry(0.25) q[2];
cx q[11],q[2];
ry(-0.25) q[2];
cx q[0],q[2];
ry(0.25) q[2];
cx q[5],q[2];
ry(-0.25) q[2];
cx q[0],q[2];
ry(0.25) q[2];
cx q[11],q[2];
ry(-0.25) q[2];
cx q[0],q[2];
ry(0.25) q[2];
cx q[2],q[11];
x q[5];
x q[0];
cx q[2],q[5];
cx q[11],q[0];
cx q[4],q[3];
cx q[12],q[7];
x q[3];
x q[7];
cx q[4],q[12];
cx q[3],q[4];
ry(-0.25) q[4];
cx q[7],q[4];
ry(0.25) q[4];
cx q[12],q[4];
ry(-0.25) q[4];
cx q[7],q[4];
ry(0.25) q[4];
cx q[3],q[4];
ry(-0.25) q[4];
cx q[7],q[4];
ry(0.25) q[4];
cx q[12],q[4];
ry(-0.25) q[4];
cx q[7],q[4];
ry(0.25) q[4];
cx q[4],q[12];
x q[3];
x q[7];
cx q[4],q[3];
cx q[12],q[7];
cx q[9],q[10];
cx q[5],q[15];
x q[10];
x q[15];
cx q[9],q[5];
cx q[10],q[9];
ry(-0.25) q[9];
cx q[15],q[9];
ry(0.25) q[9];
cx q[5],q[9];
ry(-0.25) q[9];
cx q[15],q[9];
ry(0.25) q[9];
cx q[10],q[9];
ry(-0.25) q[9];
cx q[15],q[9];
ry(0.25) q[9];
cx q[5],q[9];
ry(-0.25) q[9];
cx q[15],q[9];
ry(0.25) q[9];
cx q[9],q[5];
x q[10];
x q[15];
cx q[9],q[10];
cx q[5],q[15];
s q[6];
sx q[6];
sx q[9];
cx q[6],q[9];
rx(1.0) q[6];
rz(1.0) q[9];
cx q[6],q[9];
sxdg q[9];
sxdg q[6];
sdg q[6];
cx q[2],q[0];
cx q[9],q[3];
x q[0];
x q[3];
cx q[2],q[9];
cx q[0],q[2];
ry(-0.25) q[2];
cx q[3],q[2];
ry(0.25) q[2];
cx q[9],q[2];
ry(-0.25) q[2];
cx q[3],q[2];
ry(0.25) q[2];
cx q[0],q[2];
ry(-0.25) q[2];
cx q[3],q[2];
ry(0.25) q[2];
cx q[9],q[2];
ry(-0.25) q[2];
cx q[3],q[2];
ry(0.25) q[2];
cx q[2],q[9];
x q[0];
x q[3];
cx q[2],q[0];
cx q[9],q[3];
cx q[5],q[3];
cx q[14],q[10];
x q[3];
x q[10];
cx q[5],q[14];
cx q[3],q[5];
ry(-0.25) q[5];
cx q[10],q[5];
ry(0.25) q[5];
cx q[14],q[5];
ry(-0.25) q[5];
cx q[10],q[5];
ry(0.25) q[5];
cx q[3],q[5];
ry(-0.25) q[5];
cx q[10],q[5];
ry(0.25) q[5];
cx q[14],q[5];
ry(-0.25) q[5];
cx q[10],q[5];
ry(0.25) q[5];
cx q[5],q[14];
x q[3];
x q[10];
cx q[5],q[3];
cx q[14],q[10];
cx q[12],q[11];
cx q[10],q[9];
x q[11];
x q[9];
cx q[12],q[10];
cx q[11],q[12];
ry(-0.25) q[12];
cx q[9],q[12];
ry(0.25) q[12];
cx q[10],q[12];
ry(-0.25) q[12];
cx q[9],q[12];
ry(0.25) q[12];
cx q[11],q[12];
ry(-0.25) q[12];
cx q[9],q[12];
ry(0.25) q[12];
cx q[10],q[12];
ry(-0.25) q[12];
cx q[9],q[12];
ry(0.25) q[12];
cx q[12],q[10];
x q[11];
x q[9];
cx q[12],q[11];
cx q[10],q[9];
cx q[1],q[6];
cx q[13],q[11];
x q[6];
x q[11];
cx q[1],q[13];
cx q[6],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[13],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[6],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[13],q[1];
ry(-0.25) q[1];
cx q[11],q[1];
ry(0.25) q[1];
cx q[1],q[13];
x q[6];
x q[11];
cx q[1],q[6];
cx q[13],q[11];
cx q[1],q[2];
cx q[7],q[15];
x q[2];
x q[15];
cx q[1],q[7];
cx q[2],q[1];
ry(-0.25) q[1];
cx q[15],q[1];
ry(0.25) q[1];
cx q[7],q[1];
ry(-0.25) q[1];
cx q[15],q[1];
ry(0.25) q[1];
cx q[2],q[1];
ry(-0.25) q[1];
cx q[15],q[1];
ry(0.25) q[1];
cx q[7],q[1];
ry(-0.25) q[1];
cx q[15],q[1];
ry(0.25) q[1];
cx q[1],q[7];
x q[2];
x q[15];
cx q[1],q[2];
cx q[7],q[15];
cx q[5],q[7];
cx q[8],q[14];
x q[7];
x q[14];
cx q[5],q[8];
cx q[7],q[5];
ry(-0.25) q[5];
cx q[14],q[5];
ry(0.25) q[5];
cx q[8],q[5];
ry(-0.25) q[5];
cx q[14],q[5];
ry(0.25) q[5];
cx q[7],q[5];
ry(-0.25) q[5];
cx q[14],q[5];
ry(0.25) q[5];
cx q[8],q[5];
ry(-0.25) q[5];
cx q[14],q[5];
ry(0.25) q[5];
cx q[5],q[8];
x q[7];
x q[14];
cx q[5],q[7];
cx q[8],q[14];
s q[7];
sx q[7];
sx q[1];
cx q[7],q[1];
rx(1.0) q[7];
rz(1.0) q[1];
cx q[7],q[1];
sxdg q[1];
sxdg q[7];
sdg q[7];
cx q[9],q[13];
cx q[7],q[0];
x q[13];
x q[0];
cx q[9],q[7];
cx q[13],q[9];
ry(-0.25) q[9];
cx q[0],q[9];
ry(0.25) q[9];
cx q[7],q[9];
ry(-0.25) q[9];
cx q[0],q[9];
ry(0.25) q[9];
cx q[13],q[9];
ry(-0.25) q[9];
cx q[0],q[9];
ry(0.25) q[9];
cx q[7],q[9];
ry(-0.25) q[9];
cx q[0],q[9];
ry(0.25) q[9];
cx q[9],q[7];
x q[13];
x q[0];
cx q[9],q[13];
cx q[7],q[0];
cx q[6],q[8];
cx q[10],q[1];
x q[8];
x q[1];
cx q[6],q[10];
cx q[8],q[6];
ry(-0.25) q[6];
cx q[1],q[6];
ry(0.25) q[6];
cx q[10],q[6];
ry(-0.25) q[6];
cx q[1],q[6];
ry(0.25) q[6];
cx q[8],q[6];
ry(-0.25) q[6];
cx q[1],q[6];
ry(0.25) q[6];
cx q[10],q[6];
ry(-0.25) q[6];
cx q[1],q[6];
ry(0.25) q[6];
cx q[6],q[10];
x q[8];
x q[1];
cx q[6],q[8];
cx q[10],q[1];
s q[6];
sx q[6];
sx q[0];
cx q[6],q[0];
rx(1.0) q[6];
rz(1.0) q[0];
cx q[6],q[0];
sxdg q[0];
sxdg q[6];
sdg q[6];
cx q[10],q[0];
cx q[3],q[14];
x q[0];
x q[14];
cx q[10],q[3];
cx q[0],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[3],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[0],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[3],q[10];
ry(-0.25) q[10];
cx q[14],q[10];
ry(0.25) q[10];
cx q[10],q[3];
x q[0];
x q[14];
cx q[10],q[0];
cx q[3],q[14];
s q[15];
sx q[15];
sx q[3];
cx q[15],q[3];
rx(1.0) q[15];
rz(1.0) q[3];
cx q[15],q[3];
sxdg q[3];
sxdg q[15];
sdg q[15];
s q[13];
sx q[13];
sx q[6];
cx q[13],q[6];
rx(1.0) q[13];
rz(1.0) q[6];
cx q[13],q[6];
sxdg q[6];
sxdg q[13];
sdg q[13];
cx q[8],q[11];
cx q[2],q[1];
x q[11];
x q[1];
cx q[8],q[2];
cx q[11],q[8];
ry(-0.25) q[8];
cx q[1],q[8];
ry(0.25) q[8];
cx q[2],q[8];
ry(-0.25) q[8];
cx q[1],q[8];
ry(0.25) q[8];
cx q[11],q[8];
ry(-0.25) q[8];
cx q[1],q[8];
ry(0.25) q[8];
cx q[2],q[8];
ry(-0.25) q[8];
cx q[1],q[8];
ry(0.25) q[8];
cx q[8],q[2];
x q[11];
x q[1];
cx q[8],q[11];
cx q[2],q[1];
cx q[12],q[10];
cx q[1],q[0];
x q[10];
x q[0];
cx q[12],q[1];
cx q[10],q[12];
ry(-0.25) q[12];
cx q[0],q[12];
ry(0.25) q[12];
cx q[1],q[12];
ry(-0.25) q[12];
cx q[0],q[12];
ry(0.25) q[12];
cx q[10],q[12];
ry(-0.25) q[12];
cx q[0],q[12];
ry(0.25) q[12];
cx q[1],q[12];
ry(-0.25) q[12];
cx q[0],q[12];
ry(0.25) q[12];
cx q[12],q[1];
x q[10];
x q[0];
cx q[12],q[10];
cx q[1],q[0];
cx q[14],q[12];
cx q[15],q[1];
x q[12];
x q[1];
cx q[14],q[15];
cx q[12],q[14];
ry(-0.25) q[14];
cx q[1],q[14];
ry(0.25) q[14];
cx q[15],q[14];
ry(-0.25) q[14];
cx q[1],q[14];
ry(0.25) q[14];
cx q[12],q[14];
ry(-0.25) q[14];
cx q[1],q[14];
ry(0.25) q[14];
cx q[15],q[14];
ry(-0.25) q[14];
cx q[1],q[14];
ry(0.25) q[14];
cx q[14],q[15];
x q[12];
x q[1];
cx q[14],q[12];
cx q[15],q[1];
cx q[4],q[10];
cx q[8],q[14];
x q[10];
x q[14];
cx q[4],q[8];
cx q[10],q[4];
ry(-0.25) q[4];
cx q[14],q[4];
ry(0.25) q[4];
cx q[8],q[4];
ry(-0.25) q[4];
cx q[14],q[4];
ry(0.25) q[4];
cx q[10],q[4];
ry(-0.25) q[4];
cx q[14],q[4];
ry(0.25) q[4];
cx q[8],q[4];
ry(-0.25) q[4];
cx q[14],q[4];
ry(0.25) q[4];
cx q[4],q[8];
x q[10];
x q[14];
cx q[4],q[10];
cx q[8],q[14];
cx q[3],q[13];
cx q[2],q[4];
x q[13];
x q[4];
cx q[3],q[2];
cx q[13],q[3];
ry(-0.25) q[3];
cx q[4],q[3];
ry(0.25) q[3];
cx q[2],q[3];
ry(-0.25) q[3];
cx q[4],q[3];
ry(0.25) q[3];
cx q[13],q[3];
ry(-0.25) q[3];
cx q[4],q[3];
ry(0.25) q[3];
cx q[2],q[3];
ry(-0.25) q[3];
cx q[4],q[3];
ry(0.25) q[3];
cx q[3],q[2];
x q[13];
x q[4];
cx q[3],q[13];
cx q[2],q[4];
s q[0];
sx q[0];
sx q[1];
cx q[0],q[1];
rx(1.0) q[0];
rz(1.0) q[1];
cx q[0],q[1];
sxdg q[1];
sxdg q[0];
sdg q[0];
s q[15];
sx q[15];
sx q[8];
cx q[15],q[8];
rx(1.0) q[15];
rz(1.0) q[8];
cx q[15],q[8];
sxdg q[8];
sxdg q[15];
sdg q[15];
cx q[11],q[9];
cx q[13],q[0];
x q[9];
x q[0];
cx q[11],q[13];
cx q[9],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[13],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[9],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[13],q[11];
ry(-0.25) q[11];
cx q[0],q[11];
ry(0.25) q[11];
cx q[11],q[13];
x q[9];
x q[0];
cx q[11],q[9];
cx q[13],q[0];
cx q[14],q[10];
cx q[6],q[5];
x q[10];
x q[5];
cx q[14],q[6];
cx q[10],q[14];
ry(-0.25) q[14];
cx q[5],q[14];
ry(0.25) q[14];
cx q[6],q[14];
ry(-0.25) q[14];
cx q[5],q[14];
ry(0.25) q[14];
cx q[10],q[14];
ry(-0.25) q[14];
cx q[5],q[14];
ry(0.25) q[14];
cx q[6],q[14];
ry(-0.25) q[14];
cx q[5],q[14];
ry(0.25) q[14];
cx q[14],q[6];
x q[10];
x q[5];
cx q[14],q[10];
cx q[6],q[5];
s q[15];
sx q[15];
sx q[6];
cx q[15],q[6];
rx(1.0) q[15];
rz(1.0) q[6];
cx q[15],q[6];
sxdg q[6];
sxdg q[15];
sdg q[15];
cx q[0],q[2];
cx q[14],q[4];
x q[2];
x q[4];
cx q[0],q[14];
cx q[2],q[0];
ry(-0.25) q[0];
cx q[4],q[0];
ry(0.25) q[0];
cx q[14],q[0];
ry(-0.25) q[0];
cx q[4],q[0];
ry(0.25) q[0];
cx q[2],q[0];
ry(-0.25) q[0];
cx q[4],q[0];
ry(0.25) q[0];
cx q[14],q[0];
ry(-0.25) q[0];
cx q[4],q[0];
ry(0.25) q[0];
cx q[0],q[14];
x q[2];
x q[4];
cx q[0],q[2];
cx q[14],q[4];
cx q[10],q[12];
cx q[5],q[11];
x q[12];
x q[11];
cx q[10],q[5];
cx q[12],q[10];
ry(-0.25) q[10];
cx q[11],q[10];
ry(0.25) q[10];
cx q[5],q[10];
ry(-0.25) q[10];
cx q[11],q[10];
ry(0.25) q[10];
cx q[12],q[10];
ry(-0.25) q[10];
cx q[11],q[10];
ry(0.25) q[10];
cx q[5],q[10];
ry(-0.25) q[10];
cx q[11],q[10];
ry(0.25) q[10];
cx q[10],q[5];
x q[12];
x q[11];
cx q[10],q[12];
cx q[5],q[11];
s q[12];
sx q[12];
sx q[10];
cx q[12],q[10];
rx(1.0) q[12];
rz(1.0) q[10];
cx q[12],q[10];
sxdg q[10];
sxdg q[12];
sdg q[12];
s q[4];
sx q[4];
sx q[1];
cx q[4],q[1];
rx(1.0) q[4];
rz(1.0) q[1];
cx q[4],q[1];
sxdg q[1];
sxdg q[4];
sdg q[4];
s q[9];
sx q[9];
sx q[4];
cx q[9],q[4];
rx(1.0) q[9];
rz(1.0) q[4];
cx q[9],q[4];
sxdg q[4];
sxdg q[9];
sdg q[9];
cx q[11],q[6];
cx q[8],q[2];
x q[6];
x q[2];
cx q[11],q[8];
cx q[6],q[11];
ry(-0.25) q[11];
cx q[2],q[11];
ry(0.25) q[11];
cx q[8],q[11];
ry(-0.25) q[11];
cx q[2],q[11];
ry(0.25) q[11];
cx q[6],q[11];
ry(-0.25) q[11];
cx q[2],q[11];
ry(0.25) q[11];
cx q[8],q[11];
ry(-0.25) q[11];
cx q[2],q[11];
ry(0.25) q[11];
cx q[11],q[8];
x q[6];
x q[2];
cx q[11],q[6];
cx q[8],q[2];
cx q[3],q[7];
cx q[11],q[15];
x q[7];
x q[15];
cx q[3],q[11];
cx q[7],q[3];
ry(-0.25) q[3];
cx q[15],q[3];
ry(0.25) q[3];
cx q[11],q[3];
ry(-0.25) q[3];
cx q[15],q[3];
ry(0.25) q[3];
cx q[7],q[3];
ry(-0.25) q[3];
cx q[15],q[3];
ry(0.25) q[3];
cx q[11],q[3];
ry(-0.25) q[3];
cx q[15],q[3];
ry(0.25) q[3];
cx q[3],q[11];
x q[7];
x q[15];
cx q[3],q[7];
cx q[11],q[15];
s q[2];
sx q[2];
sx q[9];
cx q[2],q[9];
rx(1.0) q[2];
rz(1.0) q[9];
cx q[2],q[9];
sxdg q[9];
sxdg q[2];
sdg q[2];
s q[6];
sx q[6];
sx q[9];
cx q[6],q[9];
rx(1.0) q[6];
rz(1.0) q[9];
cx q[6],q[9];
sxdg q[9];
sxdg q[6];
sdg q[6];
cx q[9],q[6];
cx q[1],q[13];
x q[6];
x q[13];
cx q[9],q[1];
cx q[6],q[9];
ry(-0.25) q[9];
cx q[13],q[9];
ry(0.25) q[9];
cx q[1],q[9];
ry(-0.25) q[9];
cx q[13],q[9];
ry(0.25) q[9];
cx q[6],q[9];
ry(-0.25) q[9];
cx q[13],q[9];
ry(0.25) q[9];
cx q[1],q[9];
ry(-0.25) q[9];
cx q[13],q[9];
ry(0.25) q[9];
cx q[9],q[1];
x q[6];
x q[13];
cx q[9],q[6];
cx q[1],q[13];
cx q[15],q[5];
cx q[13],q[12];
x q[5];
x q[12];
cx q[15],q[13];
cx q[5],q[15];
ry(-0.25) q[15];
cx q[12],q[15];
ry(0.25) q[15];
cx q[13],q[15];
ry(-0.25) q[15];
cx q[12],q[15];
ry(0.25) q[15];
cx q[5],q[15];
ry(-0.25) q[15];
cx q[12],q[15];
ry(0.25) q[15];
cx q[13],q[15];
ry(-0.25) q[15];
cx q[12],q[15];
ry(0.25) q[15];
cx q[15],q[13];
x q[5];
x q[12];
cx q[15],q[5];
cx q[13],q[12];
cx q[3],q[7];
cx q[1],q[11];
x q[7];
x q[11];
cx q[3],q[1];
cx q[7],q[3];
ry(-0.25) q[3];
cx q[11],q[3];
ry(0.25) q[3];
cx q[1],q[3];
ry(-0.25) q[3];
cx q[11],q[3];
ry(0.25) q[3];
cx q[7],q[3];
ry(-0.25) q[3];
cx q[11],q[3];
ry(0.25) q[3];
cx q[1],q[3];
ry(-0.25) q[3];
cx q[11],q[3];
ry(0.25) q[3];
cx q[3],q[1];
x q[7];
x q[11];
cx q[3],q[7];
cx q[1],q[11];
cx q[13],q[0];
cx q[4],q[5];
x q[0];
x q[5];
cx q[13],q[4];
cx q[0],q[13];
ry(-0.25) q[13];
cx q[5],q[13];
ry(0.25) q[13];
cx q[4],q[13];
ry(-0.25) q[13];
cx q[5],q[13];
ry(0.25) q[13];
cx q[0],q[13];
ry(-0.25) q[13];
cx q[5],q[13];
ry(0.25) q[13];
cx q[4],q[13];
ry(-0.25) q[13];
cx q[5],q[13];
ry(0.25) q[13];
cx q[13],q[4];
x q[0];
x q[5];
cx q[13],q[0];
cx q[4],q[5];
s q[10];
sx q[10];
sx q[5];
cx q[10],q[5];
rx(1.0) q[10];
rz(1.0) q[5];
cx q[10],q[5];
sxdg q[5];
sxdg q[10];
sdg q[10];
cx q[2],q[1];
cx q[12],q[14];
x q[1];
x q[14];
cx q[2],q[12];
cx q[1],q[2];
ry(-0.25) q[2];
cx q[14],q[2];
ry(0.25) q[2];
cx q[12],q[2];
ry(-0.25) q[2];
cx q[14],q[2];
ry(0.25) q[2];
cx q[1],q[2];
ry(-0.25) q[2];
cx q[14],q[2];
ry(0.25) q[2];
cx q[12],q[2];
ry(-0.25) q[2];
cx q[14],q[2];
ry(0.25) q[2];
cx q[2],q[12];
x q[1];
x q[14];
cx q[2],q[1];
cx q[12],q[14];
s q[0];
sx q[0];
sx q[7];
cx q[0],q[7];
rx(1.0) q[0];
rz(1.0) q[7];
cx q[0],q[7];
sxdg q[7];
sxdg q[0];
sdg q[0];
cx q[0],q[1];
cx q[6],q[8];
x q[1];
x q[8];
cx q[0],q[6];
cx q[1],q[0];
ry(-0.25) q[0];
cx q[8],q[0];
ry(0.25) q[0];
cx q[6],q[0];
ry(-0.25) q[0];
cx q[8],q[0];
ry(0.25) q[0];
cx q[1],q[0];
ry(-0.25) q[0];
cx q[8],q[0];
ry(0.25) q[0];
cx q[6],q[0];
ry(-0.25) q[0];
cx q[8],q[0];
ry(0.25) q[0];
cx q[0],q[6];
x q[1];
x q[8];
cx q[0],q[1];
cx q[6],q[8];
cx q[14],q[15];
cx q[7],q[12];
x q[15];
x q[12];
cx q[14],q[7];
cx q[15],q[14];
ry(-0.25) q[14];
cx q[12],q[14];
ry(0.25) q[14];
cx q[7],q[14];
ry(-0.25) q[14];
cx q[12],q[14];
ry(0.25) q[14];
cx q[15],q[14];
ry(-0.25) q[14];
cx q[12],q[14];
ry(0.25) q[14];
cx q[7],q[14];
ry(-0.25) q[14];
cx q[12],q[14];
ry(0.25) q[14];
cx q[14],q[7];
x q[15];
x q[12];
cx q[14],q[15];
cx q[7],q[12];

