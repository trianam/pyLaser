#!/usr/bin/python

# Copyright (C) 2015  Stefano Martina, Nicoletta Granchi

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate
from mpl_toolkits.mplot3d import axes3d
import matplotlib.animation as ani

#constants
kMin = 1.
kMax = 1000.
kStep = 0.1
k = 5.    #decay rate in laser cavity (beam trasmission) (>0)

g1Min = 1.
g1Max = 1000.
g1Step = 10.
g1 = 1.   #decay rates of atomic polarization (>0)

g2Min = 1.
g2Max = 1000.
g2Step = 10.
g2 = 1.   #decay rates for population inversion (>0)

lMin = 11.  #pumping energy parameter (in R)
lMax = 100.
lStep = 0.01
lInt = 10.

l = lMin

singleStartPoint = [0.5, 0.5, 0.5]
radius = 0.0001
graphLimit = [[singleStartPoint[0]-radius, singleStartPoint[1]-radius, singleStartPoint[2]-radius],[singleStartPoint[0]+radius, singleStartPoint[1]+radius, singleStartPoint[2]+radius]]
viewLimit = [[-3., -3., -7.],[3., 3., 7.]]
#graphLimit = [[-0.5, -0.5, -0.5],[0.5, 0.5, 0.5]]
#viewLimit = [[-2, -2, -2],[2, 2, 2]]
#graphLimit = [[-2, -2, -2],[2, 2, 2]]
#viewLimit = [[-10, -10, -10],[10, 10, 10]]

gridNum = 2

tMin = 0.1
tMax = 100.
tStep = 0.1
t = 100.  #integration time
integrationSteps = 10000

multipleStartPoints = []
for x in np.linspace(graphLimit[0][0], graphLimit[1][0], gridNum):
    for y in np.linspace(graphLimit[0][1], graphLimit[1][1], gridNum):
        for z in np.linspace(graphLimit[0][2], graphLimit[1][2], gridNum):
            multipleStartPoints.append([x,y,z])


#E = S[0]
#P = S[1]
#D = S[2]

#full system
#Ed = k(P-E)
#Pd = g1(ED-P)
#Dd = g2(l+1-D-lEP)
maxwell = lambda k, g1, g2, l: lambda S, t:[k*(S[1]-S[0]),g1*(S[0]*S[2]-S[1]), g2*(l+1.-S[2]-l*S[0]*S[1])]

#jacobian
#  -k       P       0
#  g1D    -g1P     g1E
# -g2lP   -g2lE     g2
maxwellJac = lambda k, g1, g2, l: lambda S, t:[[-k, S[1], 0], [g1*S[2], -g1*S[1], g1*S[0]], [-g2*l*S[1], -g2*l*S[0], g2]]

#adiabatic elimination system
#Ed = kE((l+1)/(lE^2+1) -1)
maxwellAdiabaticEl = lambda k, l: lambda E, t: k*l*(E-E**3)/(l*E*E+1.)
adiabaticP = lambda l: lambda E: E*(l+1.)/(l*E*E+1.)
adiabaticD = lambda l: lambda E: (l+1.)/(l*E*E+1.)

fig = plt.figure(figsize=(13, 7));
ax = fig.gca(projection='3d')
fig.canvas.set_window_title('Maxwell-Bloch')
ax.set_title('Study of Maxwell-Bloch equations trajectories')
ax.set_xlabel('$E$')
ax.set_ylabel('$P$')
ax.set_zlabel('$D$')
ax.set_xlim(viewLimit[0][0], viewLimit[1][0])
ax.set_ylim(viewLimit[0][1], viewLimit[1][1])
ax.set_zlim(viewLimit[0][2], viewLimit[1][2])

line = []
lineA = []
for i in range(0, len(multipleStartPoints)):
    line[len(line):len(line)], = [plt.plot([],[],[])]
    lineA[len(lineA):len(lineA)], = [plt.plot([],[],[])]

plt.figtext(0.7, 0.80, '$\dot{E} = \kappa(P-E)$')
plt.figtext(0.7, 0.75, '$\dot{P} = \gamma_1(ED-P)$')
plt.figtext(0.7, 0.70, '$\dot{D} = \gamma_2(\lambda+1-D-\lambda EP)$')
kText = plt.figtext(0.7, 0.65, '')
g1Text = plt.figtext(0.7, 0.60, '')
g2Text = plt.figtext(0.7, 0.55, '')
lText = plt.figtext(0.7, 0.50, '')
tText = plt.figtext(0.7, 0.45, '')

pause = True
reverse = False
adiabatic = False
single = True

def onClick(event):
#    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata))

    global pause
    global reverse
    global adiabatic
    global single
    global k
    global g1
    global g2
    global l
    global t
    if event.key == ' ':
        pause ^= True
    
    elif event.key == 'r':
        reverse ^= True

    elif event.key == 'a':
        adiabatic ^= True

    elif event.key == 'z':
        single ^= True

    elif event.key == '2':
        if k < kMax:
            k = min(k + kStep, kMax)

    elif event.key == '1':
        if k > kMin:
            k = max(k - kStep, kMin)

    elif event.key == '4':
        if g1 < g1Max:
            g1 = min(g1 + g1Step, g1Max)

    elif event.key == '3':
        if g1 > g1Min:
            g1 = max(g1 - g1Step, g1Min)

    elif event.key == '6':
        if g2 < g2Max:
            g2 = min(g2 + g2Step, g2Max)

    elif event.key == '5':
        if g2 > g2Min:
            g2 = max(g2 - g2Step, g2Min)

    elif event.key == '8':
        if l < lMax:
            l = min(l + lStep, lMax)

    elif event.key == '7':
        if l > lMin:
            l = max(l - lStep, lMin)

    elif event.key == '0':
        if t < tMax:
            t = min(t + tStep, tMax)

    elif event.key == '9':
        if t > tMin:
            t = max(t - tStep, tMin)

    elif event.key == 'q':
        exit()

#fig.canvas.mpl_connect('button_press_event', onClick)
fig.canvas.mpl_connect('key_press_event', onClick)

def init():
    for i in range(0, len(multipleStartPoints)):
        line[i].set_data([], [])
        line[i].set_3d_properties([])
        lineA[i].set_data([], [])
        lineA[i].set_3d_properties([])
    kText.set_text('')
    g1Text.set_text('')
    g2Text.set_text('')
    lText.set_text('')
    tText.set_text('')
    return line, lineA, kText, g1Text, g2Text, lText

def makeGenerator(lMin, lMax, lStep):
    def generator():
        global l
        if not reverse:
            l = lMin
        else:
            l = lMax
            
        while l <= lMax+lStep and l >= lMin-lStep:
            if not pause:
                if not reverse:
                    l = l + lStep
                else:
                    l = l - lStep
            yield l
    return generator

def step(l):
    global adiabatic
    global single
    global k
    global g1
    global g2
    global t
    ts = np.linspace(0.0, t, integrationSteps)
    i = 0
    for sp in multipleStartPoints:
        if single:
            if i==0:
                state = scipy.integrate.odeint(maxwell(k, g1, g2, l), singleStartPoint, ts, Dfun=maxwellJac(k, g1, g2, l))#, mxstep=1000)

                Es = state[:,0]
                Ps = state[:,1]
                Ds = state[:,2]
            else:
                Es = []
                Ps = []
                Ds = []
            
        else:    
            state = scipy.integrate.odeint(maxwell(k, g1, g2, l), sp, ts, Dfun=maxwellJac(k, g1, g2, l))#, mxstep=1000)

            Es = state[:,0]
            Ps = state[:,1]
            Ds = state[:,2]

            
        line[i].set_data(Es,Ps)
        line[i].set_3d_properties(Ds)

        if adiabatic:
            if single:
                if i==0:
                    state = scipy.integrate.odeint(maxwellAdiabaticEl(k, l), singleStartPoint[0], ts)#, mxstep=1000)
                    Es = state[:,0]

                    Ps = list(map(adiabaticP(l), Es))
                    Ds = list(map(adiabaticD(l), Es))

                else:
                    Es = []
                    Ps = []
                    Ds = []

            else:
                state = scipy.integrate.odeint(maxwellAdiabaticEl(k, l), sp[0], ts)#, mxstep=1000)
                Es = state[:,0]

                Ps = list(map(adiabaticP(l), Es))
                Ds = list(map(adiabaticD(l), Es))

        else:
            Es = []
            Ps = []
            Ds = []

        lineA[i].set_data(Es,Ps)
        lineA[i].set_3d_properties(Ds)

        
        i = i + 1
            
    kText.set_text('$\kappa$ = %.2f' % k)
    g1Text.set_text('$\gamma_1$ = %.2f' % g1)
    g2Text.set_text('$\gamma_2$ = %.2f' % g2)
    lText.set_text('$\lambda$ = %.2f' % l)
    tText.set_text('$t$ = %.2f' % t)
    return line, lineA, kText, g1Text, g2Text, lText, tText


anim = ani.FuncAnimation(fig, step, frames=makeGenerator(lMin, lMax, lStep), init_func=init, blit=False, repeat=True) #, interval=lInt

plt.show()

