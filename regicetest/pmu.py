#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 BayLibre
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
import time

from regicepmu.pmu import PMU, PMUCounter
from regicepmu.perf import CPULoad, MemoryLoad

class BL123_CPULoad(CPULoad):
    def _enable(self):
        self.cnt0 = self.pmu.enable_event(0)
        self.cnt1 = self.pmu.enable_event(1)
        self.cnt0_val = 0
        self.cnt1_val = 0

    def _disable(self):
        self.pmu.disable_event(self.cnt0)
        self.pmu.disable_event(self.cnt1)

    def get_value(self):
        cnt0_val = self.cnt0.read()
        cnt1_val = self.cnt1.read()

        value = float((cnt1_val - self.cnt1_val) / (cnt0_val - self.cnt0_val))
        value *= 100

        self.cnt0_val = cnt0_val
        self.cnt1_val = cnt1_val

        return value

class BL123_MemoryLoad(MemoryLoad):
    def _enable(self):
        self.cnt0 = self.pmu.enable_event(2)
        self.cnt1 = self.pmu.enable_event(3)
        self.cnt0_val = 0
        self.cnt1_val = 0

    def _disable(self):
        self.pmu.disable_event(self.cnt0)
        self.pmu.disable_event(self.cnt1)

    def get_value(self):
        cnt0_val = self.cnt0.read()
        cnt1_val = self.cnt1.read()

        value = float((cnt1_val - self.cnt1_val) / (cnt0_val - self.cnt0_val))
        value *= 100

        self.cnt0_val = cnt0_val
        self.cnt1_val = cnt1_val

        return value

class BL123PMUCounter(PMUCounter):
    def __init__(self, pmu, index):
        cnt = eval("pmu.PMU.CNT{}".format(index))
        self.cntevt = eval("pmu.PMU.CNTEVT{}".format(index))
        self.random = True
        super(BL123PMUCounter, self).__init__(pmu, cnt, support_event=True)

    def _enable(self):
        self.cntevt.EN |= 1
        return True

    def _disable(self):
        self.cntevt.EN &= 0

    def _enabled(self):
        return self.cntevt.EN == 1

    def _set_event(self, event_id):
        self.cntevt.EVT = event_id
        return True

    def update_counter(self):
        value = int(self.register)
        if time.time() % 20 < 10:
            if self.event_id == 0:
                value += 1000
            if self.event_id == 1:
                value += 800
            if self.event_id == 2:
                value += 1000
            if self.event_id == 3:
                value += 500
        else:
            if self.event_id == 0:
                value += 1000
            if self.event_id == 1:
                value += 50
            if self.event_id == 2:
                value += 1000
            if self.event_id == 3:
                value += 100
        if self.random:
            value += random.randint(50, 200)
        self.register.write(value)

    def read(self):
        if self._enabled():
            self.update_counter()
        return super(BL123PMUCounter, self).read()

class BL123PMU(PMU):
    def __init__(self, device):
        super(BL123PMU, self).__init__(device, 'CPU PMU')
        self.PMU = device.PMU0
        for index in range(0, 6):
            BL123PMUCounter(self, index)
        BL123_CPULoad(self, 0)
        BL123_CPULoad(self, 1)
        BL123_MemoryLoad(self)
        self.events = {
            0 : ['TOTAL_CYCCNT', 'Total of number cpu cycle'],
            1 : ['CYCCNT', 'Executed cpu cycle'],
            2 : ['TOTAL_MEMCNT', 'Total number of memory cycle'],
            3 : ['MEMCNT', 'Memory access cycle'],
        }

    def _enable(self):
        self.PMU.CTRL.EN |= 1

    def _disable(self):
        self.PMU.CTRL.EN &= 0

    def _enabled(self):
        return self.PMU.CTRL.EN == 1

    def reset(self):
        self.PMU.CTRL.RST |= 1

    def pause(self):
        self.PMU.CTRL.PAUSE |= 1

    def resume(self):
        self.PMU.CTRL.RST &= 0
