OPENQASM 2.0;
include "qelib1.inc";
qreg q[5];
rz(pi/2) q[0];
sx q[0];
rz(pi/2) q[0];
rz(2.0) q[0];
rz(pi/2) q[1];
sx q[1];
rz(pi/2) q[1];
rz(2.0) q[1];
cx q[0],q[1];
rz(9.172838187819544) q[1];
cx q[0],q[1];
rz(pi/2) q[2];
sx q[2];
rz(pi/2) q[2];
rz(2.0) q[2];
cx q[0],q[2];
rz(9.172838187819544) q[2];
cx q[0],q[2];
cx q[1],q[2];
rz(9.172838187819544) q[2];
cx q[1],q[2];
rz(pi/2) q[3];
sx q[3];
rz(pi/2) q[3];
rz(2.0) q[3];
cx q[0],q[3];
rz(9.172838187819544) q[3];
cx q[0],q[3];
cx q[1],q[3];
rz(9.172838187819544) q[3];
cx q[1],q[3];
cx q[2],q[3];
rz(9.172838187819544) q[3];
cx q[2],q[3];
rz(pi/2) q[4];
sx q[4];
rz(pi/2) q[4];
rz(2.0) q[4];
cx q[0],q[4];
rz(9.172838187819544) q[4];
cx q[0],q[4];
rz(pi/2) q[0];
sx q[0];
rz(pi/2) q[0];
rz(2.0) q[0];
cx q[1],q[4];
rz(9.172838187819544) q[4];
cx q[1],q[4];
rz(pi/2) q[1];
sx q[1];
rz(pi/2) q[1];
rz(2.0) q[1];
cx q[0],q[1];
rz(9.172838187819544) q[1];
cx q[0],q[1];
cx q[2],q[4];
rz(9.172838187819544) q[4];
cx q[2],q[4];
rz(pi/2) q[2];
sx q[2];
rz(pi/2) q[2];
rz(2.0) q[2];
cx q[0],q[2];
rz(9.172838187819544) q[2];
cx q[0],q[2];
cx q[1],q[2];
rz(9.172838187819544) q[2];
cx q[1],q[2];
cx q[3],q[4];
rz(9.172838187819544) q[4];
cx q[3],q[4];
rz(pi/2) q[3];
sx q[3];
rz(pi/2) q[3];
rz(2.0) q[3];
cx q[0],q[3];
rz(9.172838187819544) q[3];
cx q[0],q[3];
cx q[1],q[3];
rz(9.172838187819544) q[3];
cx q[1],q[3];
cx q[2],q[3];
rz(9.172838187819544) q[3];
cx q[2],q[3];
rz(pi/2) q[4];
sx q[4];
rz(pi/2) q[4];
rz(2.0) q[4];
cx q[0],q[4];
rz(9.172838187819544) q[4];
cx q[0],q[4];
rz(0) q[0];
sx q[0];
rz(3.201281720836594) q[0];
sx q[0];
rz(3*pi) q[0];
cx q[1],q[4];
rz(9.172838187819544) q[4];
cx q[1],q[4];
rz(0) q[1];
sx q[1];
rz(4.019447055125821) q[1];
sx q[1];
rz(3*pi) q[1];
cx q[2],q[4];
rz(9.172838187819544) q[4];
cx q[2],q[4];
rz(0) q[2];
sx q[2];
rz(3.7491547474739484) q[2];
sx q[2];
rz(3*pi) q[2];
cx q[3],q[4];
rz(9.172838187819544) q[4];
cx q[3],q[4];
rz(0) q[3];
sx q[3];
rz(3.816726279726188) q[3];
sx q[3];
rz(3*pi) q[3];
rz(0) q[4];
sx q[4];
rz(4.069683106165397) q[4];
sx q[4];
rz(3*pi) q[4];
cx q[3],q[4];
cx q[2],q[3];
cx q[1],q[2];
cx q[0],q[1];
rz(0) q[0];
sx q[0];
rz(3.437259766662308) q[0];
sx q[0];
rz(3*pi) q[0];
rz(0) q[1];
sx q[1];
rz(4.047823826890452) q[1];
sx q[1];
rz(3*pi) q[1];
rz(0) q[2];
sx q[2];
rz(3.268743225132954) q[2];
sx q[2];
rz(3*pi) q[2];
rz(0) q[3];
sx q[3];
rz(3.3693274145516527) q[3];
sx q[3];
rz(3*pi) q[3];
rz(0) q[4];
sx q[4];
rz(3.4247355253747855) q[4];
sx q[4];
rz(3*pi) q[4];
