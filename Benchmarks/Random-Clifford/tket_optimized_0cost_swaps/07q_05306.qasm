OPENQASM 2.0;
include "qelib1.inc";

qreg q[7];
u3(1.5*pi,0.0*pi,0.5*pi) q[0];
u3(0.0*pi,-0.5*pi,2.0*pi) q[1];
u3(0.0*pi,-0.5*pi,1.0*pi) q[2];
u3(1.0*pi,-0.5*pi,3.5*pi) q[3];
u3(0.5*pi,0.0*pi,1.0*pi) q[4];
u3(1.5*pi,-0.5*pi,0.5*pi) q[5];
u3(1.0*pi,-0.5*pi,1.0*pi) q[6];
cx q[4],q[1];
u3(0.0*pi,-0.5*pi,1.0*pi) q[1];
cx q[4],q[3];
cx q[0],q[4];
u3(0.5*pi,0.0*pi,1.0*pi) q[3];
cx q[1],q[0];
cx q[5],q[4];
u3(0.0*pi,-0.5*pi,1.0*pi) q[0];
cx q[6],q[4];
cx q[3],q[6];
u3(0.0*pi,-0.5*pi,1.0*pi) q[4];
cx q[2],q[4];
u3(0.0*pi,-0.5*pi,1.0*pi) q[6];
cx q[2],q[1];
u3(0.0*pi,-0.5*pi,1.0*pi) q[4];
u3(0.0*pi,-0.5*pi,1.0*pi) q[1];
u3(0.5*pi,0.0*pi,0.5*pi) q[2];
cx q[5],q[1];
cx q[5],q[0];
u3(0.0*pi,-0.5*pi,1.0*pi) q[1];
cx q[6],q[1];
cx q[1],q[3];
u3(0.5*pi,0.0*pi,0.5*pi) q[6];
u3(0.0*pi,-0.5*pi,1.0*pi) q[3];
cx q[6],q[5];
cx q[2],q[3];
u3(0.5*pi,-0.5*pi,0.5*pi) q[6];
cx q[3],q[5];
cx q[5],q[2];
cx q[6],q[3];
u3(0.5*pi,-0.5*pi,1.0*pi) q[2];
u3(0.0*pi,-0.5*pi,1.0*pi) q[3];
cx q[0],q[2];
cx q[3],q[0];
cx q[0],q[6];
u3(0.5*pi,-0.5*pi,0.5*pi) q[3];
cx q[2],q[3];
u3(0.5*pi,-0.5*pi,1.0*pi) q[6];
u3(0.0*pi,-0.5*pi,1.0*pi) q[3];
cx q[6],q[3];
cx q[2],q[6];
u3(0.0*pi,-0.5*pi,1.0*pi) q[3];
u3(0.5*pi,-0.5*pi,0.5*pi) q[2];
u3(0.0*pi,-0.5*pi,1.0*pi) q[6];
swap q[6],q[2];
