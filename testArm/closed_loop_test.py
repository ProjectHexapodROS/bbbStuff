#!/usr/bin/env python
"""
"""

from adc_utilities import *
import logging
from pid import PIDController
from pwm_utilities import *
import time
from utilities import *

log = logging.getLogger(__name__)

def percentageClamp(control):
  return clamp((-1., 1.), control)

def mapControlToPwmPair(control):
  control = percentageClamp(control)
  mag = 1. - abs(control)  # the 1 - here is because pwm duty 0 corresponds to full speed instead of stop
  result = getPercentageIntoRange((1800000, 3500000), mag)
  return (PWM_PERIOD, int(result)) if control > 0 else (int(result), PWM_PERIOD)

def executePwmPair(pair):
  log.debug("Commanding %s" % str(pair))
  writePwm(P9_22, pair[0])
  writePwm(P9_14, PWM_PERIOD - pair[0])  # LED
  writePwm(P9_21, pair[1])
  writePwm(P9_16, PWM_PERIOD - pair[1])  # LED

def main():
  pid = PIDController(1., 0, .1)
  lastTime = time.time()
  while True:
    reading = readAin(AIN3, ELBOW_RANGE)
    log.debug("Read: %s" % reading)
    now = time.time()
    control = pid.update(.5, reading, now - lastTime)
    pair = mapControlToPwmPair(control)
    executePwmPair(pair)
    lastTime = now
    time.sleep(.1)  # because the valve response rate is 10Hz


if __name__ == "__main__":
  from utilties import safeRun
  safeRun(main)
