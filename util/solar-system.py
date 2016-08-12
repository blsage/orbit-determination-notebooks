# Solar System visualization
# based on the JPL DE405 ephemeris
# M. Faison  2013-07-10

import numpy
from ephemPy import Ephemeris as Ephemeris_BC
from visual import *

class Ephemeris(Ephemeris_BC):

    def __init__(self, *args, **kwargs):
        Ephemeris_BC.__init__(self, *args, **kwargs)
        self.AUFAC = 1.0/self.constants.AU
        self.EMFAC = 1.0/(1.0+self.constants.EMRAT)

    def position(self, t, target, center):
        pos = self._position(t, target)
        if center != self.SS_BARY:
            pos = pos - self._position(t, center)
        return pos
    
    def _position(self, t, target):
        if target == self.SS_BARY:
            return numpy.zeros((3,), numpy.float64)
        if target == self.EM_BARY:
            return Ephemeris_BC.position(self, t, self.EARTH)*self.AUFAC
        pos = Ephemeris_BC.position(self, t, target)*self.AUFAC
        if target == self.EARTH:
            mpos = Ephemeris_BC.position(self, t, self.MOON)*self.AUFAC
            pos = pos - mpos*self.EMFAC
        elif target == self.MOON:
            epos = Ephemeris_BC.position(self, t, self.EARTH)*self.AUFAC
            pos = pos + epos - pos*self.EMFAC
        return pos


ephem = Ephemeris('405')

# Let's start on August 11, 1972
# JD 2441540.5

t = 2441540.5
eps = radians(-23.439)
x = vector(1,0,0)

mercury = ephem.position(t, 0, 10)
venus = ephem.position(t, 1, 10)
earth = ephem.position(t, 2, 10)
mars = ephem.position(t, 3, 10)
jupiter = ephem.position(t, 4, 10)
saturn = ephem.position(t, 5, 10)

mercury = rotate(mercury, eps, x)
venus = rotate(venus, eps, x)
mars = rotate(mars, eps, x)
earth = rotate(earth, eps, x)
jupiter = rotate(jupiter, eps, x)
saturn = rotate(saturn, eps, x)




scene = display(title='Orbit', width=1000, height=800, center=(0.,0.,0.), up=(0,0,1))
    
sunsphere = sphere(pos=vector(0.,0.,0.), radius = 0.1, color=color.yellow)
mercurysphere = sphere(pos = mercury, radius = 0.005, color=color.green)
mercurytrail = curve(color=color.green)
venussphere = sphere(pos = venus, radius = 0.01, color=color.white)
venustrail = curve(color=color.white)
earthsphere = sphere(pos = earth, radius = 0.01, color=color.blue)
earthtrail = curve(color=color.blue)
marssphere = sphere(pos = mars, radius = 0.01, color = color.red)
marstrail = curve(color=color.red)
jupitersphere = sphere(pos = jupiter, radius = 0.05, color=color.magenta)
jupitertrail = curve(color=color.magenta)
saturnsphere = sphere(pos = saturn, radius = 0.05, color=color.orange)
saturntrail = curve(color=color.orange)

#xaxis = arrow(pos=(0.,0.,0.), axis=(0.5,0.,0.), opacity=0.6, shaftwidth=0.02, color=color.red)
#yaxis = arrow(pos=(0.,0.,0.), axis=(0.,0.5,0.), opacity=0.6, shaftwidth=0.02, color=color.green)
#zaxis = arrow(pos=(0.,0.,0.), axis=(0.,0.,0.5), opacity=0.6, shaftwidth=0.02, color=color.blue)



time_step = 0.05  #julian days

while true:
    rate(1000)
    t = t + time_step
    
    mercury = ephem.position(t, 0, 10)
    venus = ephem.position(t, 1, 10)
    earth = ephem.position(t, 2, 10)
    mars = ephem.position(t, 3, 10)
    jupiter = ephem.position(t, 4, 10)
    saturn = ephem.position(t, 5, 10)

    mercury = rotate(mercury, eps, x)
    venus = rotate(venus, eps, x)
    mars = rotate(mars, eps, x)
    earth = rotate(earth, eps, x)
    jupiter = rotate(jupiter, eps, x)
    saturn = rotate(saturn, eps, x)



    mercurysphere.pos = mercury
    mercurytrail.append(pos=mercury)
    venussphere.pos = venus
    venustrail.append(pos=venus)
    earthsphere.pos = earth
    earthtrail.append(pos=earth)
    marssphere.pos = mars
    marstrail.append(pos=mars)
    jupitersphere.pos = jupiter
    jupitertrail.append(pos=jupiter)
    saturnsphere.pos = saturn
    saturntrail.append(pos=saturn)

    



