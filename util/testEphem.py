#-----------------------------------------------------------------------------
# Copyright (c) 2008  Raymond L. Buvel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Edit these selections for the appropriate ephemeris.

ephemerisNumber = '405'
testFileName = '/Users/faison/testpo.405' 

#-----------------------------------------------------------------------------
import numpy
try:
    # Try to use the extension module
    from ephemExt import Ephemeris as Ephemeris_BC

except ImportError:
    # The extension does not exist so use the Python module
    from ephemPy import Ephemeris as Ephemeris_BC

import ephemUtils

#-----------------------------------------------------------------------------
# The JPL Fortran test program "testeph.f" uses AU as the distance unit.  Also
# a number of centers are used in the test data.  Define a sub-class that
# performs the transformations provided in the Fortran code.

timeSum = 0
timeCount = 0
from time import time as _time

class Ephemeris(Ephemeris_BC):

    def __init__(self, *args, **kwargs):
        Ephemeris_BC.__init__(self, *args, **kwargs)

        # Pre-compute some frequently used factors
        self.AUFAC = 1.0/self.constants.AU
        self.EMFAC = 1.0/(1.0+self.constants.EMRAT)


    def state(self, t, target, center):
        # Instrument this method to collect performance information on the
        # Python and Pyrex implementations.
        global timeSum, timeCount
        st = _time()
        PV = self._state(t, target)

        if center != self.SS_BARY:
            PV = PV - self._state(t, center)

        et = _time()
        timeSum += et-st
        timeCount += 1
        return PV


    def position(self, t, target, center):
        pos = self._position(t, target)

        if center != self.SS_BARY:
            pos = pos - self._position(t, center)

        return pos


    def _state(self, t, target):
        if target == self.SS_BARY:
            return numpy.zeros((6,), numpy.float64)

        if target == self.EM_BARY:
            return Ephemeris_BC.state(self, t, self.EARTH)*self.AUFAC

        PV = Ephemeris_BC.state(self, t, target)*self.AUFAC

        if target == self.EARTH:
            mPV = Ephemeris_BC.state(self, t, self.MOON)*self.AUFAC
            PV = PV - mPV*self.EMFAC

        elif target == self.MOON:
            ePV = Ephemeris_BC.state(self, t, self.EARTH)*self.AUFAC
            PV = PV + ePV - PV*self.EMFAC

        return PV


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

#-----------------------------------------------------------------------------
# Create the ephemeris object

ephem = Ephemeris(ephemerisNumber)

#*****************************************************************************
# Almost everything above this mark is useful in user applications.
#*****************************************************************************

#-----------------------------------------------------------------------------
# Read the first record and pick up some values.

print 'Start file scan'
firstRecord = ephem.getRecord(ephem.eStartTime + 0.5*ephem.eTimeStep)

# Validate the records in the file.  Read each record and make sure the
# time values are consistent.

lastTimes = firstRecord[:2]
checkTimes = numpy.array([ephem.eTimeStep,ephem.eTimeStep])
for i in xrange(1,ephem.numRecords):
    rec = ephem.getRecord(ephem.eStartTime + (i+0.5)*ephem.eTimeStep)
    dt = rec[:2] - lastTimes 
    if (dt != checkTimes).any():
        print 'Invalid record times', i, dt
    lastTimes = rec[:2]
    
lastRecord = rec
del rec
if ephem.eStartTime != firstRecord[0] or ephem.eEndTime != lastRecord[1]:
    print 'Invalid time data'

print 'End file scan'

#-----------------------------------------------------------------------------
# This function reads the test data file and prepares a list of filtered test
# cases.  Tests that are not within the ephemeris are filtered out.
#
# See JPL Fortran test program "testeph.f" for the format of the test file.

timeSkip = []
def getTestData(fileName):
    testFile = file(fileName)
    inData = False
    lst = []
    count = 0
    for line in testFile:
        if inData:
            count += 1
            rec = line.split()
            jed = float(rec[2])

            # Verify the date conversion functions while collecting the test
            # data.  The test data has both the calendar and Julian day forms.
            ymd = tuple([int(x) for x in rec[1].split('.')])
            if (ephemUtils.julian(rec[1]) != jed or
                ephemUtils.date(jed) != ymd):
                print line
                raise ValueError('Date conversion error')

            if jed < ephem.eStartTime or jed > ephem.eEndTime:
                # Record lines where the time is out of range.  This is not
                # necessarily an error since the ephemeris may be a subset of
                # the ephemeris for which the test is built.
                timeSkip.append(line)
                continue
            t,c,x = [int(x) for x in rec[3:6]]
            val = float(rec[6])
            lst.append((jed,t,c,x,val))
        else:
            if line.startswith('EOT'):
                inData = True
    testFile.close()
    print 'Number of tests filtered =', (count-len(lst))
    return lst

#-----------------------------------------------------------------------------
# Run all of the test cases in the test data list.  Prints statistics on the
# results.  Any failed cases are added to the failList for debugging.

failList = []
posCount = 0
def runTest(testData):
    import time
    passCnt = 0
    failCnt = 0
    testCnt = 0
    failList[:] = []
    st = time.time()
    for data in testData:
        if evalTestCase(data):
            passCnt += 1
        else:
            failCnt += 1
        testCnt += 1
        if (testCnt % 1000) == 0:
            print 'Number of tests processed =', testCnt

    et = time.time()
    print 'Run time = %.3f seconds' % (et-st)
    avg = timeSum/timeCount * 1e6
    print 'timeCount = %d, average for state = %.1f usec' % (timeCount, avg)
    print 'Number of position tests =', posCount
    print 'Number of tests that pass =', passCnt
    print 'Number of tests that fail =', failCnt

#-----------------------------------------------------------------------------
# Execute and evaluate a single test case.  Returns True if the test passes.
# For test cases where a position coordinate is requested, both the state and
# position methods are tested.
#
# See JPL Fortran test program "testeph.f" for a description of the target and
# center point.

def evalTestCase(data):
    global posCount
    t = data[0]
    # Correct for Fortran indexing
    target = data[1] - 1
    center = data[2] - 1
    coord = data[3] - 1
    value = data[4]

    _pass = True

    if target == 13:
        nu = ephem.nutations(t)
        if abs(nu[coord] - value) > 1e-13:
            _pass = False
            failList.append((data, nu))
        return _pass

    if target == 14:
        lib = ephem.librations(t)
        if abs(lib[coord] - value) > 1e-13:
            _pass = False
            failList.append((data, lib))
        return _pass

    PV = ephem.state(t, target, center)

    if abs(PV[coord] - value) > 1e-13:
        _pass = False
        failList.append((data, PV))

    if coord > 2:
        return _pass

    posCount += 1
    pos = ephem.position(t, target, center)

    if abs(pos[coord] - value) > 1e-13:
        _pass = False
        failList.append((data, pos))

    return _pass

#-----------------------------------------------------------------------------
testData = getTestData(testFileName)
runTest(testData)

