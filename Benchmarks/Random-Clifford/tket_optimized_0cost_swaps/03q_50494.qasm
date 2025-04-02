OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
u3(1.0*pi,-0.5*pi,0.5*pi) q[0];
u3(1.5*pi,-0.5*pi,4.0*pi) q[1];
u3(0.0*pi,-0.5*pi,1.5*pi) q[2];
cx q[1],q[2];
u3(0.5*pi,-0.5*pi,0.5*pi) q[1];
u3(0.0*pi,-0.5*pi,1.0*pi) q[2];
cx q[0],q[2];
u3(0.5*pi,0.0*pi,0.5*pi) q[0];
cx q[2],q[1];
u3(0.5*pi,-0.5*pi,1.0*pi) q[1];
u3(0.5*pi,0.0*pi,0.5*pi) q[2];
swap q[2],q[0];
