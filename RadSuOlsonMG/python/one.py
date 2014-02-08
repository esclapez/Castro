#!/usr/bin/env python

from pylab import *
from read_gnu import *
import cPickle as pickle

Er0_3, x, t_3, = read_gnu_file('../run-common/Er0_0031.gnu')
Er1_3, x, t_3, = read_gnu_file('../run-common/Er1_0031.gnu')
eint_3, x, t_3, = read_gnu_file('../run-common/eint_0031.gnu')

# Er0_30, x, t_30, = read_gnu_file('../run-common/Er0_3001.gnu')
# Er1_30, x, t_30, = read_gnu_file('../run-common/Er1_3001.gnu')
# eint_30, x, t_30, = read_gnu_file('../run-common/eint_3001.gnu')

fid = open('SOunits.p', 'rb')
units =pickle.load(fid)
fid.close()

U1_3 = Er0_3 / units['Eg']
U2_3 = Er1_3 / units['Eg']
V_3  = eint_3 / units['rhoe']

#U1_30 = Er0_30 / units['Eg']
#U2_30 = Er1_30 / units['Eg']
#V_30  = eint_30 / units['rhoe']

x = x / units['L']
t_3 = t_3 / units['time']
#t_30 = t_30 / units['time']

print 't = ', t_3

ex_3 = array([0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 2.50, 3.50, 5.00, 7.50, 10.0, 15.0, 20.0, 25.0])
eU1_3 = array([0.11343, 0.11073, 0.10717, 0.10367, 0.09692, 0.09047, 0.08433, 0.07295, 0.05802, 0.03838, 0.02435, 0.00858, 0.00250, 0.00060])
eU2_3 = array([0.40645, 0.28679, 0.15591, 0.08076, 0.01931, 0.00442, 0.00137, 0.00064, 0.00045, 0.00025, 0.00013, 0.00003, 0.00001, 0.00000])
eV_3  = array([0.61576, 0.42201, 0.21349, 0.10346, 0.02258, 0.00566, 0.00256, 0.00170, 0.00124, 0.00072, 0.00040, 0.00011, 0.00003, 0.00000])

figure(1, figsize=(7,8))

subplots_adjust(left=0.13, bottom=0.08, right=0.97, top=0.97, wspace=0,hspace=0)

subplot(311)
loglog(x,U1_3, 'k')
loglog(ex_3, eU1_3, 'ro')
xticks(visible=False)
ylabel('$U_1$')
minorticks_on()
xlim(0.2,25.6)
ylim(4.e-4, 0.2)

subplot(312)
loglog(x,U2_3, 'k')
loglog(ex_3, eU2_3, 'ro')
xticks(visible=False)
ylabel('$U_2$')
minorticks_on()
xlim(0.2,25.6)
ylim(3.e-6, 0.9)

subplot(313)
loglog(x,V_3, 'k')
loglog(ex_3, eV_3, 'ro')
xlabel('$x$')
ylabel('$V$')
minorticks_on()
xlim(0.2,25.6)
ylim(5.e-5, 3.)

draw()
show()

