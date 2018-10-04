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

from regiceclock import ClockTree, Gate, Mux, PLL, Divider, FixedClock

def MHz(freq):
    return freq * 1000 * 1000

def pll_get_freq(pll):
    PLL = pll.device.CLOCK0.PLL
    if PLL.EN == 0:
        return 0
    return pll.get_parent().get_freq() * (PLL.MULT / PLL.DIV)

class BL123ClockTree(ClockTree):
    def __init__(self, device):
        super(BL123ClockTree, self).__init__(device)
        device.tree = self
        clk0 = device.CLOCK0
        FixedClock(tree=self, name='OSC0',
                   freq=MHz(1), en_field=clk0.OSC0.EN)
        FixedClock(tree=self, name='OSC1',
                   freq=MHz(8), en_field=clk0.OSC1.EN)
        FixedClock(tree=self, name='OSC2',
                   freq=MHz(16), en_field=clk0.OSC2.EN)
        Mux(tree=self, name='PLLSRC',
            parents={0: 'OSC0', 1: 'OSC1', 2: 'OSC2'}, mux_field=clk0.PLL.SRC)
        PLL(tree=self, name='PLL', parent='PLLSRC',
            get_freq=pll_get_freq, en_field=clk0.PLL.EN)
        Mux(tree=self, name='BUS0SRC', mux_field=clk0.BUS0.SRC,
            parents={0: 'OSC0', 1: 'OSC1', 2: 'OSC2', 3: 'PLL'})
        Divider(tree=self, name='BUS0DIV', parent='BUS0SRC',
            div_field=clk0.BUS0.DIV, div_type=Divider.POWER_OF_TWO)
        Divider(tree=self, name='BUS1DIV', parent='BUS0DIV',
            div_field=clk0.BUS1.DIV, div_type=Divider.POWER_OF_TWO)
        Gate(tree=self, name='UART0', parent='BUS0DIV',
             en_field=clk0.UART0.EN)
        Gate(tree=self, name='UART1', parent='BUS0DIV',
             en_field=clk0.UART1.EN)
        Gate(tree=self, name='GPIO0', parent='BUS1DIV',
             en_field=clk0.GPIO0.EN)
        Gate(tree=self, name='GPIO1', parent='BUS1DIV',
             en_field=clk0.GPIO1.EN)
        Gate(tree=self, name='GPIO2', parent='BUS1DIV',
             en_field=clk0.GPIO2.EN)
        Gate(tree=self, name='GPIO3', parent='BUS1DIV',
             en_field=clk0.GPIO3.EN)
