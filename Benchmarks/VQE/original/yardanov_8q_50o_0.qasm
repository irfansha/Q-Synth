// Initializing random generator with seed:  0
OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
cx q[6],q[0];
cx q[2],q[4];
x q[0];
x q[4];
cx q[6],q[2];
ry(0.25) q[6];
h q[0];
cx q[6],q[0];
ry(-0.25) q[6];
h q[4];
cx q[6],q[4];
ry(0.25) q[6];
cx q[6],q[0];
ry(-0.25) q[6];
h q[2];
cx q[6],q[2];
ry(0.25) q[6];
cx q[6],q[0];
ry(-0.25) q[6];
cx q[6],q[4];
ry(0.25) q[6];
h q[4];
cx q[6],q[0];
ry(-0.25) q[6];
h q[0];
sdg q[2];
cx q[6],q[2];
h q[2];
s q[6];
sdg q[2];
x q[0];
h q[2];
x q[2];
s q[2];
x q[4];
cx q[6],q[0];
cx q[2],q[4];
cx q[6],q[7];
cx q[2],q[3];
x q[7];
x q[3];
cx q[6],q[2];
ry(0.25) q[6];
h q[7];
cx q[6],q[7];
ry(-0.25) q[6];
h q[3];
cx q[6],q[3];
ry(0.25) q[6];
cx q[6],q[7];
ry(-0.25) q[6];
h q[2];
cx q[6],q[2];
ry(0.25) q[6];
cx q[6],q[7];
ry(-0.25) q[6];
cx q[6],q[3];
ry(0.25) q[6];
h q[3];
cx q[6],q[7];
ry(-0.25) q[6];
h q[7];
sdg q[2];
cx q[6],q[2];
h q[2];
s q[6];
sdg q[2];
x q[7];
h q[2];
x q[2];
s q[2];
x q[3];
cx q[6],q[7];
cx q[2],q[3];
cx q[3],q[4];
cx q[1],q[2];
x q[4];
x q[2];
cx q[3],q[1];
ry(0.25) q[3];
h q[4];
cx q[3],q[4];
ry(-0.25) q[3];
h q[2];
cx q[3],q[2];
ry(0.25) q[3];
cx q[3],q[4];
ry(-0.25) q[3];
h q[1];
cx q[3],q[1];
ry(0.25) q[3];
cx q[3],q[4];
ry(-0.25) q[3];
cx q[3],q[2];
ry(0.25) q[3];
h q[2];
cx q[3],q[4];
ry(-0.25) q[3];
h q[4];
sdg q[1];
cx q[3],q[1];
h q[1];
s q[3];
sdg q[1];
x q[4];
h q[1];
x q[1];
s q[1];
x q[2];
cx q[3],q[4];
cx q[1],q[2];
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
cx q[2],q[7];
cx q[0],q[5];
x q[7];
x q[5];
cx q[2],q[0];
ry(0.25) q[2];
h q[7];
cx q[2],q[7];
ry(-0.25) q[2];
h q[5];
cx q[2],q[5];
ry(0.25) q[2];
cx q[2],q[7];
ry(-0.25) q[2];
h q[0];
cx q[2],q[0];
ry(0.25) q[2];
cx q[2],q[7];
ry(-0.25) q[2];
cx q[2],q[5];
ry(0.25) q[2];
h q[5];
cx q[2],q[7];
ry(-0.25) q[2];
h q[7];
sdg q[0];
cx q[2],q[0];
h q[0];
s q[2];
sdg q[0];
x q[7];
h q[0];
x q[0];
s q[0];
x q[5];
cx q[2],q[7];
cx q[0],q[5];
cx q[7],q[4];
cx q[0],q[2];
x q[4];
x q[2];
cx q[7],q[0];
ry(0.25) q[7];
h q[4];
cx q[7],q[4];
ry(-0.25) q[7];
h q[2];
cx q[7],q[2];
ry(0.25) q[7];
cx q[7],q[4];
ry(-0.25) q[7];
h q[0];
cx q[7],q[0];
ry(0.25) q[7];
cx q[7],q[4];
ry(-0.25) q[7];
cx q[7],q[2];
ry(0.25) q[7];
h q[2];
cx q[7],q[4];
ry(-0.25) q[7];
h q[4];
sdg q[0];
cx q[7],q[0];
h q[0];
s q[7];
sdg q[0];
x q[4];
h q[0];
x q[0];
s q[0];
x q[2];
cx q[7],q[4];
cx q[0],q[2];
cx q[5],q[4];
cx q[7],q[1];
x q[4];
x q[1];
cx q[5],q[7];
ry(0.25) q[5];
h q[4];
cx q[5],q[4];
ry(-0.25) q[5];
h q[1];
cx q[5],q[1];
ry(0.25) q[5];
cx q[5],q[4];
ry(-0.25) q[5];
h q[7];
cx q[5],q[7];
ry(0.25) q[5];
cx q[5],q[4];
ry(-0.25) q[5];
cx q[5],q[1];
ry(0.25) q[5];
h q[1];
cx q[5],q[4];
ry(-0.25) q[5];
h q[4];
sdg q[7];
cx q[5],q[7];
h q[7];
s q[5];
sdg q[7];
x q[4];
h q[7];
x q[7];
s q[7];
x q[1];
cx q[5],q[4];
cx q[7],q[1];
cx q[7],q[6];
cx q[4],q[2];
x q[6];
x q[2];
cx q[7],q[4];
ry(0.25) q[7];
h q[6];
cx q[7],q[6];
ry(-0.25) q[7];
h q[2];
cx q[7],q[2];
ry(0.25) q[7];
cx q[7],q[6];
ry(-0.25) q[7];
h q[4];
cx q[7],q[4];
ry(0.25) q[7];
cx q[7],q[6];
ry(-0.25) q[7];
cx q[7],q[2];
ry(0.25) q[7];
h q[2];
cx q[7],q[6];
ry(-0.25) q[7];
h q[6];
sdg q[4];
cx q[7],q[4];
h q[4];
s q[7];
sdg q[4];
x q[6];
h q[4];
x q[4];
s q[4];
x q[2];
cx q[7],q[6];
cx q[4],q[2];
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
cx q[0],q[4];
cx q[3],q[2];
x q[4];
x q[2];
cx q[0],q[3];
ry(0.25) q[0];
h q[4];
cx q[0],q[4];
ry(-0.25) q[0];
h q[2];
cx q[0],q[2];
ry(0.25) q[0];
cx q[0],q[4];
ry(-0.25) q[0];
h q[3];
cx q[0],q[3];
ry(0.25) q[0];
cx q[0],q[4];
ry(-0.25) q[0];
cx q[0],q[2];
ry(0.25) q[0];
h q[2];
cx q[0],q[4];
ry(-0.25) q[0];
h q[4];
sdg q[3];
cx q[0],q[3];
h q[3];
s q[0];
sdg q[3];
x q[4];
h q[3];
x q[3];
s q[3];
x q[2];
cx q[0],q[4];
cx q[3],q[2];
s q[7];
sx q[7];
sx q[5];
cx q[7],q[5];
rx(1.0) q[7];
rz(1.0) q[5];
cx q[7],q[5];
sxdg q[5];
sxdg q[7];
sdg q[7];
s q[4];
sx q[4];
sx q[3];
cx q[4],q[3];
rx(1.0) q[4];
rz(1.0) q[3];
cx q[4],q[3];
sxdg q[3];
sxdg q[4];
sdg q[4];
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
s q[4];
sx q[4];
sx q[5];
cx q[4],q[5];
rx(1.0) q[4];
rz(1.0) q[5];
cx q[4],q[5];
sxdg q[5];
sxdg q[4];
sdg q[4];
cx q[1],q[2];
cx q[4],q[6];
x q[2];
x q[6];
cx q[1],q[4];
ry(0.25) q[1];
h q[2];
cx q[1],q[2];
ry(-0.25) q[1];
h q[6];
cx q[1],q[6];
ry(0.25) q[1];
cx q[1],q[2];
ry(-0.25) q[1];
h q[4];
cx q[1],q[4];
ry(0.25) q[1];
cx q[1],q[2];
ry(-0.25) q[1];
cx q[1],q[6];
ry(0.25) q[1];
h q[6];
cx q[1],q[2];
ry(-0.25) q[1];
h q[2];
sdg q[4];
cx q[1],q[4];
h q[4];
s q[1];
sdg q[4];
x q[2];
h q[4];
x q[4];
s q[4];
x q[6];
cx q[1],q[2];
cx q[4],q[6];
s q[6];
sx q[6];
sx q[5];
cx q[6],q[5];
rx(1.0) q[6];
rz(1.0) q[5];
cx q[6],q[5];
sxdg q[5];
sxdg q[6];
sdg q[6];
s q[3];
sx q[3];
sx q[4];
cx q[3],q[4];
rx(1.0) q[3];
rz(1.0) q[4];
cx q[3],q[4];
sxdg q[4];
sxdg q[3];
sdg q[3];
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
s q[1];
sx q[1];
sx q[4];
cx q[1],q[4];
rx(1.0) q[1];
rz(1.0) q[4];
cx q[1],q[4];
sxdg q[4];
sxdg q[1];
sdg q[1];
s q[0];
sx q[0];
sx q[2];
cx q[0],q[2];
rx(1.0) q[0];
rz(1.0) q[2];
cx q[0],q[2];
sxdg q[2];
sxdg q[0];
sdg q[0];
cx q[7],q[0];
cx q[6],q[1];
x q[0];
x q[1];
cx q[7],q[6];
ry(0.25) q[7];
h q[0];
cx q[7],q[0];
ry(-0.25) q[7];
h q[1];
cx q[7],q[1];
ry(0.25) q[7];
cx q[7],q[0];
ry(-0.25) q[7];
h q[6];
cx q[7],q[6];
ry(0.25) q[7];
cx q[7],q[0];
ry(-0.25) q[7];
cx q[7],q[1];
ry(0.25) q[7];
h q[1];
cx q[7],q[0];
ry(-0.25) q[7];
h q[0];
sdg q[6];
cx q[7],q[6];
h q[6];
s q[7];
sdg q[6];
x q[0];
h q[6];
x q[6];
s q[6];
x q[1];
cx q[7],q[0];
cx q[6],q[1];
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
s q[7];
sx q[7];
sx q[6];
cx q[7],q[6];
rx(1.0) q[7];
rz(1.0) q[6];
cx q[7],q[6];
sxdg q[6];
sxdg q[7];
sdg q[7];
cx q[3],q[6];
cx q[1],q[4];
x q[6];
x q[4];
cx q[3],q[1];
ry(0.25) q[3];
h q[6];
cx q[3],q[6];
ry(-0.25) q[3];
h q[4];
cx q[3],q[4];
ry(0.25) q[3];
cx q[3],q[6];
ry(-0.25) q[3];
h q[1];
cx q[3],q[1];
ry(0.25) q[3];
cx q[3],q[6];
ry(-0.25) q[3];
cx q[3],q[4];
ry(0.25) q[3];
h q[4];
cx q[3],q[6];
ry(-0.25) q[3];
h q[6];
sdg q[1];
cx q[3],q[1];
h q[1];
s q[3];
sdg q[1];
x q[6];
h q[1];
x q[1];
s q[1];
x q[4];
cx q[3],q[6];
cx q[1],q[4];
cx q[4],q[3];
cx q[6],q[2];
x q[3];
x q[2];
cx q[4],q[6];
ry(0.25) q[4];
h q[3];
cx q[4],q[3];
ry(-0.25) q[4];
h q[2];
cx q[4],q[2];
ry(0.25) q[4];
cx q[4],q[3];
ry(-0.25) q[4];
h q[6];
cx q[4],q[6];
ry(0.25) q[4];
cx q[4],q[3];
ry(-0.25) q[4];
cx q[4],q[2];
ry(0.25) q[4];
h q[2];
cx q[4],q[3];
ry(-0.25) q[4];
h q[3];
sdg q[6];
cx q[4],q[6];
h q[6];
s q[4];
sdg q[6];
x q[3];
h q[6];
x q[6];
s q[6];
x q[2];
cx q[4],q[3];
cx q[6],q[2];
s q[4];
sx q[4];
sx q[5];
cx q[4],q[5];
rx(1.0) q[4];
rz(1.0) q[5];
cx q[4],q[5];
sxdg q[5];
sxdg q[4];
sdg q[4];
s q[4];
sx q[4];
sx q[7];
cx q[4],q[7];
rx(1.0) q[4];
rz(1.0) q[7];
cx q[4],q[7];
sxdg q[7];
sxdg q[4];
sdg q[4];
cx q[3],q[1];
cx q[0],q[2];
x q[1];
x q[2];
cx q[3],q[0];
ry(0.25) q[3];
h q[1];
cx q[3],q[1];
ry(-0.25) q[3];
h q[2];
cx q[3],q[2];
ry(0.25) q[3];
cx q[3],q[1];
ry(-0.25) q[3];
h q[0];
cx q[3],q[0];
ry(0.25) q[3];
cx q[3],q[1];
ry(-0.25) q[3];
cx q[3],q[2];
ry(0.25) q[3];
h q[2];
cx q[3],q[1];
ry(-0.25) q[3];
h q[1];
sdg q[0];
cx q[3],q[0];
h q[0];
s q[3];
sdg q[0];
x q[1];
h q[0];
x q[0];
s q[0];
x q[2];
cx q[3],q[1];
cx q[0],q[2];
s q[2];
sx q[2];
sx q[3];
cx q[2],q[3];
rx(1.0) q[2];
rz(1.0) q[3];
cx q[2],q[3];
sxdg q[3];
sxdg q[2];
sdg q[2];
s q[3];
sx q[3];
sx q[5];
cx q[3],q[5];
rx(1.0) q[3];
rz(1.0) q[5];
cx q[3],q[5];
sxdg q[5];
sxdg q[3];
sdg q[3];
s q[6];
sx q[6];
sx q[1];
cx q[6],q[1];
rx(1.0) q[6];
rz(1.0) q[1];
cx q[6],q[1];
sxdg q[1];
sxdg q[6];
sdg q[6];
s q[0];
sx q[0];
sx q[3];
cx q[0],q[3];
rx(1.0) q[0];
rz(1.0) q[3];
cx q[0],q[3];
sxdg q[3];
sxdg q[0];
sdg q[0];
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
s q[3];
sx q[3];
sx q[1];
cx q[3],q[1];
rx(1.0) q[3];
rz(1.0) q[1];
cx q[3],q[1];
sxdg q[1];
sxdg q[3];
sdg q[3];
s q[6];
sx q[6];
sx q[5];
cx q[6],q[5];
rx(1.0) q[6];
rz(1.0) q[5];
cx q[6],q[5];
sxdg q[5];
sxdg q[6];
sdg q[6];
s q[4];
sx q[4];
sx q[0];
cx q[4],q[0];
rx(1.0) q[4];
rz(1.0) q[0];
cx q[4],q[0];
sxdg q[0];
sxdg q[4];
sdg q[4];
s q[1];
sx q[1];
sx q[3];
cx q[1],q[3];
rx(1.0) q[1];
rz(1.0) q[3];
cx q[1],q[3];
sxdg q[3];
sxdg q[1];
sdg q[1];
s q[1];
sx q[1];
sx q[7];
cx q[1],q[7];
rx(1.0) q[1];
rz(1.0) q[7];
cx q[1],q[7];
sxdg q[7];
sxdg q[1];
sdg q[1];
s q[4];
sx q[4];
sx q[0];
cx q[4],q[0];
rx(1.0) q[4];
rz(1.0) q[0];
cx q[4],q[0];
sxdg q[0];
sxdg q[4];
sdg q[4];
cx q[1],q[6];
cx q[2],q[0];
x q[6];
x q[0];
cx q[1],q[2];
ry(0.25) q[1];
h q[6];
cx q[1],q[6];
ry(-0.25) q[1];
h q[0];
cx q[1],q[0];
ry(0.25) q[1];
cx q[1],q[6];
ry(-0.25) q[1];
h q[2];
cx q[1],q[2];
ry(0.25) q[1];
cx q[1],q[6];
ry(-0.25) q[1];
cx q[1],q[0];
ry(0.25) q[1];
h q[0];
cx q[1],q[6];
ry(-0.25) q[1];
h q[6];
sdg q[2];
cx q[1],q[2];
h q[2];
s q[1];
sdg q[2];
x q[6];
h q[2];
x q[2];
s q[2];
x q[0];
cx q[1],q[6];
cx q[2],q[0];
s q[5];
sx q[5];
sx q[1];
cx q[5],q[1];
rx(1.0) q[5];
rz(1.0) q[1];
cx q[5],q[1];
sxdg q[1];
sxdg q[5];
sdg q[5];
cx q[5],q[3];
cx q[1],q[0];
x q[3];
x q[0];
cx q[5],q[1];
ry(0.25) q[5];
h q[3];
cx q[5],q[3];
ry(-0.25) q[5];
h q[0];
cx q[5],q[0];
ry(0.25) q[5];
cx q[5],q[3];
ry(-0.25) q[5];
h q[1];
cx q[5],q[1];
ry(0.25) q[5];
cx q[5],q[3];
ry(-0.25) q[5];
cx q[5],q[0];
ry(0.25) q[5];
h q[0];
cx q[5],q[3];
ry(-0.25) q[5];
h q[3];
sdg q[1];
cx q[5],q[1];
h q[1];
s q[5];
sdg q[1];
x q[3];
h q[1];
x q[1];
s q[1];
x q[0];
cx q[5],q[3];
cx q[1],q[0];
cx q[0],q[4];
cx q[7],q[3];
x q[4];
x q[3];
cx q[0],q[7];
ry(0.25) q[0];
h q[4];
cx q[0],q[4];
ry(-0.25) q[0];
h q[3];
cx q[0],q[3];
ry(0.25) q[0];
cx q[0],q[4];
ry(-0.25) q[0];
h q[7];
cx q[0],q[7];
ry(0.25) q[0];
cx q[0],q[4];
ry(-0.25) q[0];
cx q[0],q[3];
ry(0.25) q[0];
h q[3];
cx q[0],q[4];
ry(-0.25) q[0];
h q[4];
sdg q[7];
cx q[0],q[7];
h q[7];
s q[0];
sdg q[7];
x q[4];
h q[7];
x q[7];
s q[7];
x q[3];
cx q[0],q[4];
cx q[7],q[3];
s q[2];
sx q[2];
sx q[4];
cx q[2],q[4];
rx(1.0) q[2];
rz(1.0) q[4];
cx q[2],q[4];
sxdg q[4];
sxdg q[2];
sdg q[2];
cx q[2],q[5];
cx q[6],q[1];
x q[5];
x q[1];
cx q[2],q[6];
ry(0.25) q[2];
h q[5];
cx q[2],q[5];
ry(-0.25) q[2];
h q[1];
cx q[2],q[1];
ry(0.25) q[2];
cx q[2],q[5];
ry(-0.25) q[2];
h q[6];
cx q[2],q[6];
ry(0.25) q[2];
cx q[2],q[5];
ry(-0.25) q[2];
cx q[2],q[1];
ry(0.25) q[2];
h q[1];
cx q[2],q[5];
ry(-0.25) q[2];
h q[5];
sdg q[6];
cx q[2],q[6];
h q[6];
s q[2];
sdg q[6];
x q[5];
h q[6];
x q[6];
s q[6];
x q[1];
cx q[2],q[5];
cx q[6],q[1];
s q[6];
sx q[6];
sx q[2];
cx q[6],q[2];
rx(1.0) q[6];
rz(1.0) q[2];
cx q[6],q[2];
sxdg q[2];
sxdg q[6];
sdg q[6];
s q[4];
sx q[4];
sx q[5];
cx q[4],q[5];
rx(1.0) q[4];
rz(1.0) q[5];
cx q[4],q[5];
sxdg q[5];
sxdg q[4];
sdg q[4];
cx q[1],q[4];
cx q[3],q[7];
x q[4];
x q[7];
cx q[1],q[3];
ry(0.25) q[1];
h q[4];
cx q[1],q[4];
ry(-0.25) q[1];
h q[7];
cx q[1],q[7];
ry(0.25) q[1];
cx q[1],q[4];
ry(-0.25) q[1];
h q[3];
cx q[1],q[3];
ry(0.25) q[1];
cx q[1],q[4];
ry(-0.25) q[1];
cx q[1],q[7];
ry(0.25) q[1];
h q[7];
cx q[1],q[4];
ry(-0.25) q[1];
h q[4];
sdg q[3];
cx q[1],q[3];
h q[3];
s q[1];
sdg q[3];
x q[4];
h q[3];
x q[3];
s q[3];
x q[7];
cx q[1],q[4];
cx q[3],q[7];
s q[5];
sx q[5];
sx q[7];
cx q[5],q[7];
rx(1.0) q[5];
rz(1.0) q[7];
cx q[5],q[7];
sxdg q[7];
sxdg q[5];
sdg q[5];

