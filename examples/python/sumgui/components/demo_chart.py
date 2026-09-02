#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  

import os;
import sys;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumui import ChartSpec;
from sumgui.easy import chart, label, start, window;

window("SumGUI ChartView", width=720, height=520, base_width=720, base_height=520);
label("ChartView / sum.chart/1", 20, 14, 500, 40, font_size=24, bold=True);
spec = ChartSpec.bar(["Python", "R", "C", "BASIC"], [42, 34, 27, 31], title="Same ChartSpec as sumTUI");
chart(spec, 20, 68, 680, 430);
start();
